import os
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    # base dir
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    # registry dir
    REGISTRY_PATH: Path = Path(os.getenv("DN42_REGISTRY", Path.home() / "registry")).resolve()
    
    # data/cache dir
    DATA_DIR: Path = BASE_DIR / "data"
    CACHE_DIR: Path = BASE_DIR / "cache"
    
    # output dir
    OUTPUT_ASN: Path = DATA_DIR / "asn"
    OUTPUT_GRAPH: Path = DATA_DIR / "graph"
    OUTPUT_ISP: Path = DATA_DIR / "isp"
    OUTPUT_TABLE: Path = DATA_DIR / "table"
    OUTPUT_HISTORY: Path = DATA_DIR / "history"
    
    # table cache
    CACHE_TABLE: Path = CACHE_DIR / "table"
    
    # MRT file
    MRT_FILE_V4: Path = CACHE_DIR / "master4.mrt.bz2"
    MRT_FILE_V6: Path = CACHE_DIR / "master6.mrt.bz2"
    
    # registry data
    REGISTRY_DATA: Path = REGISTRY_PATH / "data"

    def setup_dirs(self):
        for path in [
            self.DATA_DIR, self.CACHE_DIR,
            self.OUTPUT_ASN, self.OUTPUT_GRAPH, 
            self.OUTPUT_ISP, self.OUTPUT_TABLE, 
            self.OUTPUT_HISTORY, self.CACHE_TABLE,
            self.DATA_DIR / "registry", # for wizard
            self.DATA_DIR / "roa"       # for wizard
        ]:
            path.mkdir(parents=True, exist_ok=True)

settings = Settings()
