from prisma import Prisma
from .__main__ import app
from . import auth, config, plants, utils, prisma


prisma = Prisma()
