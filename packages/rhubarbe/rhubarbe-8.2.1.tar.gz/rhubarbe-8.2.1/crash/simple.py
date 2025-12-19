from dataclasses import dataclass
from dataclass_wizard import YAMLWizard

class PduHost(YAMLWizard):
    name: str

class