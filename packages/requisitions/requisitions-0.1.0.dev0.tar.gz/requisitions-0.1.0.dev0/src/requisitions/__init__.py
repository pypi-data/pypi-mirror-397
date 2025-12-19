"""
Requisitions
=======

"""

from . import ncbi
from .ncbi import (
    Entrez,
    NCBI_EMAIL,
    NCBI_TOKEN,
    USER_AGENT
)


__all__ = [
	# : modules
	#
	"ncbi",
	
	# : classes
	#
	"Entrez",
	
	# : constants
	#
    "NCBI_EMAIL",
	"NCBI_TOKEN",
    "USER_AGENT"
]

