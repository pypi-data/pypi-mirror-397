{
    "name": "Cooperator API - SomConnexio",
    "version": "16.0.1.1.2",
    "summary": """
        Expose a REST API to integrate cooperators and sponsorship to Som Connexió
        partner structure.
    """,
    "author": """
        Som Connexió SCCL,
        Coopdevs Treball SCCL
    """,
    "website": "https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio",
    "license": "AGPL-3",
    "category": "Cooperative Management",
    "depends": [
        "base_rest_somconnexio",
        "cooperator_somconnexio",
        "crm_lead_api_somconnexio",
        "res_partner_api_somconnexio"
    ],
    "data": [],
    "demo": [],
    "external_dependencies": {"python": ["stdnum"]},
    "application": False,
    "installable": True,
}
