from bloku.utils import BlockusBuilder
from blokus.models import Block
import json
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class BlockCollection(Resource):
    def get(self):
        body = BlockusBuilder()
        body.add_namespace("blokus", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.blockcollection"))
        body["items"] = []
        for db_block in Block.query.all()
            item = BlockusBuilder(
                shape = db_block.shape
            )
            item.add_control("self", url_for("api.blockitem", block=db_sensor.id))
            item.add_control("profile", BLOCK_PROFILE)
            body["items"].append(item)
        
        return Response(json.dumps(body), 200, mimetype=MASON)

class BlockItem(Resource):
    def get(self, block):
        db_block = Block.query.filter_by(id=block).first()

