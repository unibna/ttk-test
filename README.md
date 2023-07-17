# TTK Test

## I. Puzzles

Take the following exa. ple schema:

- Model: Order
	- Field: ID
- Model: OrderStatus
	- Field: ID
	- Field: Created (DateTime)
	- Field: Status (Text: Pending/Complete/Cancelled)
	- Field: OrderID (ForeignKey)

We have a database of many Orders, and each Order has one or many OrderStatus records. Each OrderStatus row has columns for created datetime and a status of Pending/Complete/Failed. The status of every Order in the database is dictated by the most recent OrderStatus.

- A Pending OrderStatus will be created for an Order when it is first created
- Complete OrderStatus is created after successful payment
- Cancelled is created if payment fails, or also if a Complete Order is refunded it is also given status Cancelled.

**Puzzle 1:**
Using the Django ORM, how would you structure a query to list all Cancelled orders in the database without changes to the schema.

**Puzzle 2:**
Given that the database may contain millions of Orders, what optimisations would you suggest to make through the use of other query techniques, technologies or schema changes to reduce burden on the database resources and improve response times.

**Note:**
Please use Django / Python for your solution. The logic and thought process demonstrated are the most important considerations rather than truly functional code, however code presentation is important as well as the technical aspect. If you cannot settle on a single perfect solution, you may also discuss alternative solutions to demonstrate your understanding of potential trade-offs as you encounter them. Of course if you consider a solution is too time consuming you are also welcome to clarify or elaborate on potential improvements or multiple solution approaches conceptually to demonstrate understanding and planned solution.

## II. Setup & Run
1. Clone project
```
	git clone https://github.com/unibna/ttk-test.git
```

2. Build container
```
	sudo docker-compose build
	sudo docker-compose up
```
After executed, API server is exposed through http://localhost:8000

3. Migrate
```
	docker-compose run app python manage.py makemigrations order
	docker-compose run app python manage.py migrate
```

4. Generate testing data
```
	docker-compose run app python manage.py setup --max-record 1000000 --order-verion 1
```
You can change the value of verion (1, 2) to generate the order verion 1 or 2 data

5. Call API
Postman Document: https://documenter.getpostman.com/view/24525080/2s946fescu#14e8cf40-1c40-4bed-a0a8-9dbf42c6c826

## III. Solutions

### Puzzle 1

To list all cancelled orders, we need to get the latest status of every order, and then, we filter the orders that have cancelled status.
In Django, the implementation of this solution is:

```
	# Get the latest status of orders
	latest_status_subquery = OrderStatus.objects.\
		filter(order=OuterRef('pk')).\
		order_by('-created_time').\
		values('status')[:1]

	# Query all orders and annotate with the latest status
	orders_with_latest_status = Order.objects.annotate(latest_status=Subquery(latest_status_subquery))

	cancelled_orders = orders_with_latest_status.filter(latest_status=OrderStatus.STATUS_CHOICES.CANCELLED.value)
```

The generated query is
```
	SELECT 
	"order_order"."id", 
	(
		SELECT U0."status" 
		FROM  "order_orderstatus" U0 
		WHERE U0."order_id" = ("order_order"."id") 
		ORDER BY U0."created_time" DESC 
		LIMIT 1
	) AS "latest_status" 
	FROM "order_order" 
	WHERE (
		SELECT U0."status" 
		FROM "order_orderstatus" U0 
		WHERE U0."order_id" = ("order_order"."id") 
		ORDER BY U0."created_time" DESC 
		LIMIT 1
	) = CANCELLED
```
___
### Puzzle 2

With the above solution, we must perform the complex query to list all cancelled orders, which can make database workload more overhead. To improve the performance and reduce the burden on database, I supposes the following approaches:

- Add field `current_status` into Order table

	Through this appoach, the minimalized query can reduce the computation of the database. We do not traverse all order status records to get the latest of each order, instead of, just filter current_status of order. 
-  Indexing by the new field `current_status`

	Combinating with the new field, the performance of retrieval action will be enhance significantly via creating an index on `current_status`. The database does not traverse on all of record, but it just scan with the status.
	
```
# Old Order schema
	class Order(models.Model):
		pass
```
```
# New Order schema
	class Order(models.Model):
		current_status = models.CharField(max_length=20,  choices=STATUS_CHOICES.to_choice_values())

		class Meta:
			indexes =  [models.Index(fields=['current_status'])]
```

-  Apply caching
	Caching frequently accessed data can greatly reduce the need to retrieve it from the database repeatedly. By storing this data in memory, you can quickly serve subsequent requests, thereby improving response times.

	Without caching, each listing request with 1000 orders takes nearly 300ms to process. This delay occurs because the API has to retrieve the data from the database, and then format the response before sending it back to the client. As the number of requests increases, the database workload also escalates, leading to potential performance bottlenecks.

	However, by implementing caching, the scenario dramatically improves. After the first request, the API caches the response, which allows subsequent identical requests to be served almost instantaneously, taking around 5 milliseconds. This significant reduction in response time is because the cached data is readily available, and the API doesn't need to recompute or query the database again. Instead, it can simply serve the pre-computed response from memory, thereby minimizing database interaction and processing overhead.

-  Apply pagination
	Implementing pagination allows you to break large result sets into smaller, manageable chunks. This way, you can retrieve only the necessary data from the database, reducing the processing time and memory consumption.