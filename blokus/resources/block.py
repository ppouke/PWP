from bloku.utils import BlockusBuilder
from blokus.models import Block
import json
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class BlockCollection(Resource):
    def get(self):
        body = utils.BlockusBuilder()

