"""
NCBI Clients
============

This module provides client interfaces for a number of NCBI endpoints.

"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Literal

import requests
from dotenv import load_dotenv


# : constants
#
load_dotenv()

NCBI_EMAIL = os.getenv("NCBI_EMAIL") or None
NCBI_TOKEN = os.getenv("NCBI_TOKEN") or None
USER_AGENT = os.getenv("USER_AGENT") or "BioReqs/1.0"


class Entrez:
    """Interface for fetching data from NCBI using E-utilities."""
    
    API_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    
    def __init__(
        self,
        email: str | None = None,
        api_key: str | None = None,
        user_agent: str | None = None
    ) -> None:
        """Constructor.

        Parameters
        ==========
        email : str
            Email address (required by NCBI for API usage)
        api_key : str | None
            NCBI API key for increased rate limits
        user_agent : str | None
            User agent string for requests

        Returns
        =======
        None
        
        """
        
        self.email = email or NCBI_EMAIL

        if not self.email:
            raise ValueError(
                "NCBI requires Entrez E-utilities API requests to include "
                "the `email` parameter."
            )
        
        self.api_key = api_key or NCBI_TOKEN
        self.user_agent = user_agent or USER_AGENT
        
        self.session = requests.Session()
        headers = {
            "Accept": "application/json, text/plain",
            "User-Agent": self.user_agent,
        }
        
        self.session.headers.update(headers)
        
        # Rate limiting: 10 requests/second with API key, 3/second without
        self.rate_limit = 0.1 if self.api_key else 0.34
        self._last_request_time = 0

    
    def __repr__(self) -> str:
        """Get a string representation of the object instance."""
        
        return (
            f"{self.__class__.__name__}("
            f"api_key={self.api_key!r}, "
            f"email={self.email!r}, "
            f"user_agent={self.user_agent!r})"
        )

    
    def _rate_limit_wait(self) -> None:
        """Enforce rate limiting between requests."""
        
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        
        self._last_request_time = time.time()
        

    def _build_params(self, **kwargs) -> dict:
        """Build common parameters for E-utilities requests."""
        
        params = {}
        
        if self.email:
            params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key
        
        params.update(kwargs)
        return params

    
    def get_refseq(
        self, 
        accession: str, 
        rettype: Literal["fasta", "gb", "gp"] = "fasta"
    ) -> str:
        """
        Fetch a RefSeq sequence by accession using EFetch.
        
        Parameters
        ==========
        accession : str
            RefSeq accession (e.g., "NM_000314", "NC_000001.11")
        rettype : str
            A string representing the desired return type.
            Currently, the following values are supported:
            
            - "fasta" (nucleotide FASTA)
            - "gb" (GenBank)
            - "gp" (GenPept protein)
        
        Returns
        =======
        str
            Sequence data in requested format
            
        """
        
        self._rate_limit_wait()
        
        if rettype == "gp" or accession.startswith(("NP_", "XP_", "YP_", "WP_")):
            database = "protein"
        else:
            database = "nucleotide"
        
        url = f"{self.API_BASE_URL}/efetch.fcgi"
        params = self._build_params(
            db=database,
            id=accession,
            rettype=rettype,
            retmode="text"
        )
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.text

    
    def save_refseq(
        self,
        accession: str,
        output_path: str | Path | None = None,
        rettype: Literal["fasta", "gb", "gp"] = "fasta",
        overwrite: bool = False
    ) -> Path:
        """
        Fetch and save RefSeq sequence to disk.
        
        Parameters
        ==========
        accession : str
            RefSeq accession (e.g., "NM_000314", "NC_000001.11"
        output_path : str | Path
            A string or path-like object representing the filepath
            to which the sequence should be saved.
        rettype : str
            A string representing the desired return type.
            Currently, the following values are supported:
            
            - "fasta" (nucleotide FASTA)
            - "gb" (GenBank)
            - "gp" (GenPept protein)
        overwrite : bool
            A boolean value indicating whether to overwrit existing file,
            if it exists. Defaults to ``False``.
        
        Returns
        =======
        Path
            A ``Path`` object representing the filepath of the saved file.
            
        """
        
        output_path = Path(f"refseqs/{accession}.{rettype}") if not output_path else Path(output_path)
        
        # Check if file exists
        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"File already exists: {output_path}. "
                f"Use overwrite=True to replace it."
            )

        if overwrite and output_path.parent.is_file():
            output_path.parent.unlink()
        
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Fetch sequence
        sequence_data = self.get_refseq(accession, rettype=rettype)
        
        # Write to file
        output_path.write_text(sequence_data)
        
        return output_path

    
    def search_nucleotide(
        self,
        term: str,
        retmax: int = 20,
        sort: str = "relevance"
    ) -> list[str]:
        """
        Search nucleotide database and return list of accessions.
        
        Parameters
        ==========
        term : str
            Search term (e.g., 'BRCA1[Gene] AND human[Organism]')
        retmax : int
            Maximum number of results to return (default: 20)
        sort : str
            Sort order: 'relevance', 'pub_date', etc. (default: 'relevance')
        
        Returns
        =======
        list[str]
            List of accession IDs
            
        """
        
        self._rate_limit_wait()
        
        url = f"{self.API_BASE_URL}/esearch.fcgi"
        params = self._build_params(
            db="nucleotide",
            term=term,
            retmax=retmax,
            sort=sort,
            retmode="json"
        )
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])

    
    def search_gene(
        self,
        term: str,
        retmax: int = 20,
        sort: str = "relevance"
    ) -> list[str]:
        """
        Search gene database and return list of gene IDs.
        
        Parameters
        ==========
        term : str
            Search term (e.g., 'BRCA1[Gene] AND human[Organism]')
        retmax : int
            Maximum number of results to return (default: 20)
        sort : str
            Sort order: 'relevance', 'pub_date', etc. (default: 'relevance')
        
        Returns
        =======
        list[str]
            List of gene IDs
            
        """
        
        self._rate_limit_wait()
        
        url = f"{self.API_BASE_URL}/esearch.fcgi"
        params = self._build_params(
            db="gene",
            term=term,
            retmax=retmax,
            sort=sort,
            retmode="json"
        )
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])

    
    def get_gene_summary(self, gene_id: str) -> dict:
        """
        Fetch gene summary using ESummary.
        
        Parameters
        ==========
        gene_id : str
            NCBI Gene ID
            
        Returns
        =======
        dict
            Gene summary data
            
        """
        
        self._rate_limit_wait()
        
        url = f"{self.API_BASE_URL}/esummary.fcgi"
        params = self._build_params(
            db="gene",
            id=gene_id,
            retmode="json"
        )
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("result", {}).get(gene_id, {})

    
    def save_gene_summary(
        self,
        gene_id: str,
        output_path: str | Path | None = None,
        overwrite: bool = False
    ) -> Path:
        """
        Fetch and save gene summary to disk as JSON.
        
        Parameters
        ==========
        gene_id : str
            NCBI Gene ID
        output_path : str | Path
            Path where the summary should be saved
        overwrite : bool
            Whether to overwrite existing file (default: False)
        
        Returns
        =======
        Path
            Path to the saved file
        """
        
        output_path = Path(output_path) or Path(f"{gene_id}")
        
        # Check if file exists
        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"File already exists: {output_path}. "
                f"Use overwrite=True to replace it."
            )
        
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Fetch summary
        summary_data = self.get_gene_summary(gene_id)
        
        # Write to file
        output_path.write_text(json.dumps(summary_data, indent=2))
        
        return output_path

    
    def link_genes_to_sequences(self, gene_id: str) -> list[str]:
        """
        Get nucleotide sequence IDs linked to a gene using ELink.
        
        Parameters
        ==========
        gene_id : str
            NCBI Gene ID
            
        Returns
        =======
        list[str]
            List of linked nucleotide sequence IDs
            
        """
        
        self._rate_limit_wait()
        
        url = f"{self.API_BASE_URL}/elink.fcgi"
        params = self._build_params(
            dbfrom="gene",
            db="nuccore",
            id=gene_id,
            retmode="json"
        )
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract linked IDs
        linksets = data.get("linksets", [])
        if not linksets:
            return []
        
        linksetdbs = linksets[0].get("linksetdbs", [])
        if not linksetdbs:
            return []
        
        return linksetdbs[0].get("links", [])

    
    def batch_fetch_sequences(
        self,
        accessions: list[str],
        output_dir: str | Path | None = None,
        rettype: Literal["fasta", "gb", "gp"] = "fasta",
        overwrite: bool = False
    ) -> list[Path]:
        """
        Fetch multiple sequences and save them to disk.
        
        Parameters
        ==========
        accessions : list[str]
            List of RefSeq accessions
        output_dir : str | Path
            Directory where sequences should be saved
        rettype : str
            Return type: 'fasta', 'gb', or 'gp'
        overwrite : bool
            Whether to overwrite existing files (default: False)
        
        Returns
        =======
        list[Path]
            List of paths to saved files
            
        """
        
        output_dir = Path("refseqs") if not output_dir else Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        
        # Determine file extension
        ext_map = {"fasta": ".fasta", "gb": ".gb", "gp": ".gp"}
        extension = ext_map.get(rettype, ".txt")
        
        for accession in accessions:
            output_path = output_dir / f"{accession}{extension}"
            
            try:
                saved_path = self.save_refseq(
                    accession=accession,
                    output_path=output_path,
                    rettype=rettype,
                    overwrite=overwrite
                )
                saved_paths.append(saved_path)
                print(f"✓ Saved: {accession}")
            except Exception as e:
                print(f"✗ Failed to fetch {accession}: {e}")
        
        return saved_paths

    
    def get_sequence_info(self, accession: str) -> dict:
        """
        Get summary information about a sequence using ESummary.
        
        Parameters
        ==========
        accession : str
            RefSeq accession
            
        Returns
        =======
        dict
            Sequence summary information
        """
        
        self._rate_limit_wait()
        
        # Determine database
        if accession.startswith(("NP_", "XP_", "YP_", "WP_")):
            database = "protein"
        else:
            database = "nucleotide"
        
        url = f"{self.API_BASE_URL}/esummary.fcgi"
        params = self._build_params(
            db=database,
            id=accession,
            retmode="json"
        )
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("result", {}).get(accession, {})
