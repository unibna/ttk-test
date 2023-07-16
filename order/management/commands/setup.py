import datetime
import random
from loguru import logger

# from django.db import transaction
from django.core.management.base import BaseCommand
from ... import models


MAX_RECORDS = 100_000


class Command(BaseCommand):

    help = "Generate testing data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-record',
            action='store',
            type=int,
            default=MAX_RECORDS,
            help='the number of record will be created'
        )
    
    def handle(self, *args, **options):
        self.max_record = options.get('max_record')
        self.generate_data()

    def generate_data(self):
        logger.info(f"Starting to generate data. Total {self.max_record}")
        total_success = 0
        total_fail = 0

        for i in range(self.max_record):
            if (i / self.max_record * 100 % 10) == 0:
                logger.info(f"Status: {i / self.max_record * 100}%")

            try:
                order = models.Order.objects.create()
                models.OrderStatus.objects.create(
                    order=order,
                    status=models.OrderStatus.STATUS_CHOICES.PENDING.value,
                )
                self.update_status(order)

                total_success += 1
            except Exception as e: 
                total_fail += 1
                logger.error(f"Failed to insert new order. Index {i}. Error: {e}")
        logger.info("Status: 100%")
    
        logger.info(f"Total new inserted order: {total_success}")
        logger.info(f"Total failed inserted order: {total_fail}")

    def add_status(self):
        pass

    def update_status(self, order):
        x = random.randint(1,3)
        try:
            if x == 1:
                models.OrderStatus.objects.create(
                    order=order,
                    status=models.OrderStatus.STATUS_CHOICES.CANCELLED.value,
                )
            elif x == 2:
                models.OrderStatus.objects.create(
                    order=order,
                    status=models.OrderStatus.STATUS_CHOICES.COMPLETED.value,
                )
            elif x == 3:
                models.OrderStatus.objects.create(
                    order=order,
                    status=models.OrderStatus.STATUS_CHOICES.COMPLETED.value,
                )
                models.OrderStatus.objects.create(
                    order=order,
                    status=models.OrderStatus.STATUS_CHOICES.CANCELLED.value,
                )
        except Exception as e:
            logger.error(f"Failed to insert new order. Order: {order.id}. Error: {e}")
