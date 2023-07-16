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
cd ttk-test
sudo docker-compose build
sudo docker-compose up
```
After executed, the API server will be runnning at http://localhost:8000

3. Generate testing data
```
docker-compose run app python manage.py setup --max-record 1000000
```

4. Call API
In the API server, I have 4 endpoints to demonstrate for the above challenge:
- Create order: POST http://localhost:8000/order
- Update order: PUT http://localhost:8000/order/<id>
- Get order detail: GET http://localhost:8000/order/<id>
- List order: GET http://localhost:8000/order

Postman Document link: https://documenter.getpostman.com/view/24525080/2s946fescu



## III. Solution
### Puzzle 1:
To solve puzzle 1, Django provide a method to query related fields by using double underscore notation. For instance,
```
orders_queryset = models.Order.objects.prefetch_related().filter(order_statuses__status='CANCELLED')
```
The generated query is
```
SELECT 
  "order_order"."id" 
FROM 
  "order_order" 
  INNER JOIN "order_orderstatus" ON (
    "order_order"."id" = "order_orderstatus"."order_id"
  ) 
WHERE 
  "order_orderstatus"."status" = 'CANCELLED' 
```
The proposed solution that involves joining two tables through the order id without altering the existing schema can help us to optimize performance and minimize the number of queries sent to the database. This approach will help us achieve better efficiency and enhance overall system performance.
You can find the implementation in `ttk/order/views.py -> class OrderAPI -> function get(...)`.
*Note*: To make it more general, there is some different between document and code.
___
### Puzzle 2:
When aiming to enhance response time and optimize the database's workload, various approaches can be considered. Some of the key strategies include:
1. Optimizing the query
2. Applying database solutions
3. Optimizing data structure and algorithm
4. Restructuring the software architect
5. Applying asynchronous, or concorrency programming
6. Implementing the caching system
7. Upgrade systems, and hardware resources

In the test scope, I decided to implement the following techniques to solve the puzzle:
1.  Pagination
2.  Indexing 
3. Cache
   
**Approach 1: Pagination**

Implementing pagination allows you to break large result sets into smaller, manageable chunks. This way, you can retrieve only the necessary data from the database, reducing the processing time and memory consumption. 

 **Approach 2: Indexing**

Properly indexing the database tables based on the frequently used columns can significantly speed up data retrieval operations. Indexes facilitate faster search and filtering, resulting in improved query performance.
I defined an index on two fields: `status`,  `created_time`, and `order_id` in the `OrderStatus` model base on the requirement of the test . 
```
	class  Meta:
		indexes =  [
			models.Index(fields=['status',  'created_time',  'order_id'])
		]
```
This approach can improve performance for certain types of queries:
- **Filtering**:

When performing queries that filter based on the indexed fields, the database can use the index to quickly locate the relevant rows. For example, if the user filter orders by status in frequently, the index allows the database to efficiently narrow down the relevant rows without performing a full table scan.
- **Sorting**: If the user need to find the oldest or newest orders, the indexing with `created_time` can speed up the sorting process. The index allows the database to retrieve the data in the required order, reducing the need for expensive sorting operations.
- **Joining**: If we perform queries that involve joining the `OrderStatus` model with other models on the indexed fields, the index can enhance the join performance. Indexes facilitate efficient lookups in both the parent (`Order`) and child (`OrderStatus`) tables during the join. 

**Trade-off:**
- As I mentioned above, indexing is very helpful in the retrieval context. On the other side, modification actions like insert, update or delete can be slow down. This may lead to increased write latency in write-heavy workloads. 
- Besides, indexing requires additional storage space. As indexes are data structures, they consume disk space. Adding indexes on multiple columns can significantly increase the database's storage requirements.

**Approach 3: Cache**

Caching frequently accessed data can greatly reduce the need to retrieve it from the database repeatedly. By storing this data in memory, you can quickly serve subsequent requests, thereby improving response times.
Without caching, each listing request with 1000 orders takes nearly 1 second to process. This delay occurs because the API has to retrieve the data from the database, and then format the response before sending it back to the client. As the number of requests increases, the database workload also escalates, leading to potential performance bottlenecks.
However, by implementing caching, the scenario dramatically improves. After the first request, the API caches the response, which allows subsequent identical requests to be served almost instantaneously, taking around 5 milliseconds. This significant reduction in response time is because the cached data is readily available, and the API doesn't need to recompute or query the database again. Instead, it can simply serve the pre-computed response from memory, thereby minimizing database interaction and processing overhead.

**Trade-off:**
- Depending on the caching strategy and expiration settings, there might be a lag between updates in the database and the cached data becoming up-to-date. Therefore, we should consider to define the suitable caching time.
- Caching frequently accessed data in memory can increase memory consumption. Depending on the size of the cached data and the number of cached items, it might impact server memory usage.