# app/routers/user_route.py

import logging
from fastapi import APIRouter,HTTPException
from app.constants.route_paths import RoutePaths
from app.constants.route_tags import RouteTags
from app.utils.extract_data import extract_data
from pathlib import Path
import subprocess
import time
from app.utils.file_system import FileSystem

class TestRouter():
    def __init__(self):
        self.router = APIRouter(prefix=RoutePaths.API_PREFIX)
        self.setup_routes()

    def setup_routes(self):
        @self.router.get(RoutePaths.TESTS, tags=[RouteTags.TESTS])  # Update the path to include the prefix
        async def tests():
            try:
                start = time.time()
                test_command = ["pytest", 'tests']
                subprocess.call(test_command)
                create_converage_commnad = ['coverage', 'json', '-i', '--pretty-print']
                subprocess.check_output(create_converage_commnad)
                time.sleep(1.0)

                coverage_totals = extract_data(path=Path("coverage.json"))
                end = time.time()
                elapsed = end - start
                coverage_totals.update({'elapsed_time': elapsed})
                # Delete coverage file after use
                FileSystem().delete_file(file_path='coverage.json')
                return coverage_totals
            except Exception as e:
                logging.error("Error in setup_route class tests method.")
                raise HTTPException(status_code=500, detail="Error running pytest: {}".format(str(e)))