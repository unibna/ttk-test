import datetime
import random
from loguru import logger

# from django.db import transaction
from django.core.management.base import BaseCommand
from ... import models


MAX_RECORDS = 10


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
        parser.add_argument(
            '--order-version',
            action='store',
            type=int,
            default=1,
            help='version can be 1 or 2'
        )
    
    def handle(self, *args, **options):
        self.max_record = options.get('max_record')
        self.version = options.get('order_version')
        if self.version == 1:
            self.generate_data_1()
        elif self.version == 2:
            self.generate_data_2()

    def generate_data_1(self):
        logger.info(f"Starting to generate data. Version 1. Total {self.max_record}")
        total_success = 0
        total_fail = 0

        for i in range(self.max_record):
            if (i / self.max_record * 100 % 10) == 0:
                logger.info(f"Status: {i / self.max_record * 100}%")

            try:
                order = models.Order.objects.create()
                models.OrderStatus.objects.create(
                    order=order,
                    status=models.STATUS_CHOICES.PENDING.value,
                )
                self.update_status(order, models.OrderStatus)

                total_success += 1
            except Exception as e: 
                total_fail += 1
                logger.error(f"Failed to insert new order. Index {i}. Error: {e}")
        logger.info("Status: 100%")
    
        logger.info(f"Total new inserted order: {total_success}")
        logger.info(f"Total failed inserted order: {total_fail}")

    def generate_data_2(self):
        logger.info(f"Starting to generate data. Version 2. Total {self.max_record}")
        total_success = 0
        total_fail = 0

        for i in range(self.max_record):
            if (i / self.max_record * 100 % 10) == 0:
                logger.info(f"Status: {i / self.max_record * 100}%")

            try:
                order = models.Order2.objects.create()
                models.OrderStatus2.objects.create(
                    order=order,
                    status=models.STATUS_CHOICES.PENDING.value,
                )
                self.update_status(order, models.OrderStatus2)

                total_success += 1
            except Exception as e: 
                total_fail += 1
                logger.error(f"Failed to insert new order. Index {i}. Error: {e}")
        logger.info("Status: 100%")
    
        logger.info(f"Total new inserted order: {total_success}")
        logger.info(f"Total failed inserted order: {total_fail}")

    def update_status(self, order, status_model):
        x = random.randint(1,3)
        try:
            if x == 1:
                status_model.objects.create(
                    order=order,
                    status=models.STATUS_CHOICES.CANCELLED.value,
                )
            elif x == 2:
                status_model.objects.create(
                    order=order,
                    status=models.STATUS_CHOICES.COMPLETED.value,
                )
            elif x == 3:
                status_model.objects.create(
                    order=order,
                    status=models.STATUS_CHOICES.COMPLETED.value,
                )
                status_model.objects.create(
                    order=order,
                    status=models.STATUS_CHOICES.CANCELLED.value,
                )
        except Exception as e:
            logger.error(f"Failed to insert new order. Order: {order.id}. Error: {e}")
