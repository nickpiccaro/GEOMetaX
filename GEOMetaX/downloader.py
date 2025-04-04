import os
import requests
import csv
import sys
from pathlib import Path


def get_data_dir():
    """Returns the path to the data directory within the installed package."""
    return Path(__file__).parent / "data"


def download_file(url, folder, filename):
    """Downloads a file from a given URL and saves it in the specified folder."""
    file_path = folder / filename
    try:
        response = requests.get(url, allow_redirects=True)  # Allow redirects in case of issues
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Downloaded and saved {filename} in {folder}")
        else:
            print(f"Failed to download {url} (Status code: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")


def fetch_chromatin_remodelers_and_synonyms(output_csv):
    """Fetches chromatin remodelers and their synonyms from the Harmonizome API."""
    base_url = "https://maayanlab.cloud/Harmonizome"
    chromatin_remodelers_url = f"{base_url}/api/1.0/gene_set/chromatin+remodeling/GO+Biological+Process+Annotations+2023"
    
    try:
        response = requests.get(chromatin_remodelers_url)
        response.raise_for_status()
        data = response.json()
        associations = data.get("associations", [])
        
        chromatin_data = []
        
        for association in associations:
            gene_symbol = association["gene"]["symbol"]
            gene_url = f"{base_url}{association['gene']['href']}"
            
            gene_response = requests.get(gene_url)
            gene_response.raise_for_status()
            gene_data = gene_response.json()
            
            synonyms = gene_data.get("synonyms", [])
            chromatin_data.append({
                "chromatin_remodeler": gene_symbol,
                "synonyms": ", ".join(synonyms) if synonyms else ""
            })
        
        with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["chromatin_remodeler", "synonyms"])
            writer.writeheader()
            writer.writerows(chromatin_data)
        
        print(f"Data successfully saved to {output_csv}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def install_data():
    """Downloads required data and organizes it into directories."""
    print("GEOMetaX | Installing data...")
    data_dir = get_data_dir()
    os.makedirs(data_dir / "unparsed_factor_data", exist_ok=True)
    os.makedirs(data_dir / "unparsed_ontology_data", exist_ok=True)
    os.makedirs(data_dir / "parsed_factor_data", exist_ok=True)
    os.makedirs(data_dir / "parsed_ontology_data", exist_ok=True)

    factor_urls = [
        "https://ftp.ncbi.nih.gov/gene/DATA/gene_info.gz",
        "https://guolab.wchscu.cn/AnimalTFDB4_static/download/TF_list_final/Homo_sapiens_TF",
    ]
    factor_filenames = ["gene_info.gz", "Homo_sapiens_TF.csv"]

    ontology_urls = [
        "https://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt",
        "https://github.com/EBISPOT/efo/releases/download/current/efo.owl",
        "http://purl.obolibrary.org/obo/uberon/uberon-full.json"
    ]
    ontology_filenames = ["cellosaurus.txt", "efo.owl", "uberon-full.json"]

    # Download factor-related data
    for url, filename in zip(factor_urls, factor_filenames):
        download_file(url, data_dir / "unparsed_factor_data", filename)
    
    # Fetch chromatin remodelers and their synonyms
    fetch_chromatin_remodelers_and_synonyms(data_dir / "parsed_factor_data/chromatin_remodelers.csv")
    
    # Download ontology data
    for url, filename in zip(ontology_urls, ontology_filenames):
        download_file(url, data_dir / "unparsed_ontology_data", filename)


if __name__ == "__main__":
    install_data()