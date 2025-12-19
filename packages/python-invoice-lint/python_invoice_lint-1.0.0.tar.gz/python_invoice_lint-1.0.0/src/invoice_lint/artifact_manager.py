import os
import shutil
import zipfile
import requests
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

CACHE_DIR = Path.home() / ".cache" / "invoice-lint"
REPO_OWNER = "ConnectingEurope"
REPO_NAME = "eInvoicing-EN16931"

class ArtifactManager:
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_artifact_path(self, version: str) -> Path:
        """
        Returns the path to the directory containing the artifacts for the given version.
        If not cached, downloads it first.
        """
        version_dir = self.cache_dir / version
        if version_dir.exists():
            return version_dir
        
        self.download_artifact(version)
        return version_dir

    def download_artifact(self, version: str):
        """
        Downloads the artifact for the given version from GitHub.
        """
        logger.info(f"Downloading artifacts for version {version}...")
        
        # Try exact version first, then with 'validation-' prefix
        tags_to_try = [version]
        if not version.startswith("validation-"):
            tags_to_try.append(f"validation-{version}")
            
        success = False
        for tag in tags_to_try:
            url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/tags/{tag}.zip"
            try:
                logger.info(f"Trying url: {url}")
                response = requests.get(url, stream=True)
                if response.status_code == 404:
                    continue
                response.raise_for_status()
                success = True
                break
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to download from {url}: {e}")
                continue

        if not success:
             raise ValueError(f"Could not download artifact for version {version}. Tried tags: {tags_to_try}")

        zip_path = self.cache_dir / f"{version}.zip"
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract
        extract_dir = self.cache_dir / version
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True) # Ensure it exists or is recreated
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Cleanup zip
        os.remove(zip_path)
        
        logger.info(f"Downloaded and extracted to {extract_dir}")

    def list_local_versions(self):
        return [d.name for d in self.cache_dir.iterdir() if d.is_dir()]
