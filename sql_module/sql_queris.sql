--1) select category.name, count(*) as film_counts 
--from category left join 
--film_category on category.category_id=film_category.category_id 
--group by category.name order by film_counts desc;


--2) select actor.actor_id, actor.first_name, actor.last_name, count(rental.rental_id) as rented_amount from
--actor left join film_actor on actor.actor_id = film_actor.actor_id
--left join film on film_actor.film_id = film.film_id
--left join inventory on film.film_id = inventory.film_id
--left join rental on inventory.inventory_id = rental.inventory_id group by actor.actor_id order by rented_amount desc limit 10;



--3) select category.name, sum(payment.amount) as total from 
--category inner join film_category on category.category_id=film_category.category_id
--inner join film on film_category.film_id=film.film_id
--inner join inventory on film.film_id=inventory.film_id
--inner join rental on inventory.inventory_id=rental.inventory_id 
--inner join payment on rental.rental_id = payment.rental_id group by category.name order by total desc limit 1;

--4) select film.title from film left join inventory on inventory.film_id = film.film_id where inventory.film_id is null;


--5) with actor_child_category_view as (select actor_id, count(*) as actor_film_count 
--from film_actor act inner join film_category cat on act.film_id = cat.film_id 
--where category_id = (select category_id from category where name = 'Children') group by actor_id)
--select actor.first_name || ' ' || actor.last_name as full_name, actor_film_count from actor_child_category_view inner join actor on actor_child_category_view.actor_id=actor.actor_id 
--where actor_film_count in (select distinct actor_film_count from actor_child_category_view order by actor_film_count desc limit 3) 
--order by actor_film_count desc, full_name;



--6) select city.city, count(case when customer.active = 1 then 1 end)as active_customers, 
--                     count(case when customer.active = 0 then 1 end)as inactive_customers from customer 
--   inner join address on customer.address_id=address.address_id 
--   inner join city on address.city_id=city.city_id group by city.city;



--7)select category.name, extract (hour from sum(rental.return_date - rental.rental_date)) as total_rent_hours from
--(select city_id, city from city where lower(city) like 'a%' or city like '%-%') as city_query inner join address on city_query.city_id=address.city_id
--inner join customer on address.address_id=customer.address_id
--inner join rental on customer.customer_id=rental.customer_id
--inner join inventory on rental.inventory_id=inventory.inventory_id
--inner join film_category on inventory.film_id=film_category.film_id
--inner join category on film_category.category_id=category.category_id group by category.name order by total_rent_hours desc limit 1;

