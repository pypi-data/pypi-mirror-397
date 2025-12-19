import csv
import random
import sys

import typer
from icat_plus_client.models.session import Session

from data import dataset, session

performance_app = typer.Typer(help="Performance workbench commands")


def get_role(user: Session):
    if user.is_administrator:
        return "administrator"
    if user.is_instrument_scientist:
        return "instrumentScientist"
    return "user"


@performance_app.command("dataset")
def do_performance_datasetworkbench(
    tokens: str = typer.Option(..., "-t", "--token", help="Comma separated list of ICAT tokens"),
    investigation_ids: str | None = typer.Option(
        None,
        "--investigation-ids",
        "-i",
        help="Comma separated list of investigation IDs (optional)",
    ),
    output: str | None = typer.Option(
        None,
        "-o",
        "--output",
        help="CSV output file path. Example: myfile.csv",
    ),
):
    user_tokens = tokens.split(",")
    investigation_id_list = investigation_ids.split(",")

    fields = [
        "role",
        "user",
        "investigation_id",
        "time",
        "datasets",
    ]

    # Always write to stdout
    stdout_writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter="\t")
    stdout_writer.writeheader()

    file_writer = None
    f = None

    if output:
        f = open(output, "w", newline="")
        file_writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        file_writer.writeheader()

    try:
        for token in user_tokens:
            user_session: Session = session.get_info(token)
            role = get_role(user_session.user)

            for investigation_id in investigation_id_list:
                datasets, duration = dataset.get_datasets(
                    session_id=token,
                    investigation_ids=investigation_id,
                    limit="100",
                    dataset_type="acquisition",
                    nested=True,
                    skip=str(random.randint(0, 1800)),
                )
                row = {
                    "role": role,
                    "user": user_session.user.username,
                    "investigation_id": investigation_id,
                    "time": duration,
                    "datasets": len(datasets),
                }

                stdout_writer.writerow(row)

                if file_writer:
                    file_writer.writerow(row)
    finally:
        if f:
            f.close()
