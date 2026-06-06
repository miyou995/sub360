from django.db import migrations

BRANCHES = {
    "main_construction": [
        "Asbestos remediation",
        "Waterproofing / sealing",
        "Track construction",
        "Structural construction (Hochbau)",
        "Road construction",
        "Civil engineering (Tiefbau)",
        "Tunnel construction",
    ],
    "ancillary_construction": [
        "Construction cleaning",
        "Floor coverings",
        "Fire protection",
        "Electrical installation",
        "Joint sealing",
        "Garden & landscaping",
        "Building insulation",
        "Building envelope",
        "Scaffolding",
        "HVAC + plumbing (HLKKS)",
        "Timber construction",
        "Insulation trade",
        "Painting & glazing",
        "Tiling & open construction",
        "Joinery",
        "Plastering & gypsum",
    ],
    "planning_construction": [
        "Architecture planning",
        "Building design",
        "Electrical engineering",
        "Building technology",
        "Geomatics",
    ],
    "technology_industry": [
        "Plant construction",
        "Elevator assembly",
        "Mechanical engineering",
        "Metal construction",
        "Pipeline construction",
        "Switchgear construction",
        "Sprinkler systems",
        "Steel construction",
    ],
}

EXECUTION_TYPES = [
    "Demolition",
    "New build",
    "Planning",
    "Renovation",
    "Conversion",
]


def seed_catalogue(apps, schema_editor):
    pass  # Data is now loaded via apps/projects/fixtures/branches.json and execution_types.json


def unseed_catalogue(apps, schema_editor):
    pass  # Reverse is a no-op; remove fixtures manually if needed


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_catalogue, unseed_catalogue),
    ]
