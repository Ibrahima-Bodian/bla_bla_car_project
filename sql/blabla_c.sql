--
-- PostgreSQL database dump
--

CREATE database blabla_c;

CREATE TABLE public.cars (
    car_id integer NOT NULL,
    maker character varying(50),
    co2_code character varying(10),
    colour character varying(30),
    year smallint,
    plate character varying(20)
);


ALTER TABLE public.cars OWNER TO postgres;

CREATE TABLE public.cities (
    city_id integer NOT NULL,
    city_name character varying(60),
    state character varying(60),
    country character varying(60)
);


ALTER TABLE public.cities OWNER TO postgres;

CREATE TABLE public.luggage_types (
    luggage_type_id integer NOT NULL,
    type character varying(15)
);


ALTER TABLE public.luggage_types OWNER TO postgres;

CREATE TABLE public.member_car (
    member_car_id integer NOT NULL,
    member_id character varying(20),
    car_id integer
);


ALTER TABLE public.member_car OWNER TO postgres;

CREATE TABLE public.members (
    member_id character varying(20) NOT NULL,
    first_name character varying(60),
    last_name character varying(60),
    gender character(1),
    mobile_number character varying(30),
    email character varying(120),
    inscription_date date,
    birthdate date,
    is_ride_owner smallint,
    license_driving_number character varying(40),
    license_driving_date date,
    pet_preference character varying(5),
    smoking_preference character varying(5),
    bank_account character varying(34)
);


ALTER TABLE public.members OWNER TO postgres;

CREATE TABLE public.messages (
    message_id character varying(20) NOT NULL,
    sender_id character varying(20),
    receiver_id character varying(20),
    body text
);


ALTER TABLE public.messages OWNER TO postgres;

CREATE TABLE public.ratings (
    rating_id character varying(20) NOT NULL,
    rating_giver_id character varying(20),
    rating_receiver_id character varying(20),
    comments text,
    grade integer
);


ALTER TABLE public.ratings OWNER TO postgres;

CREATE TABLE public.request_status (
    request_status_id integer NOT NULL,
    status character varying(20)
);


ALTER TABLE public.request_status OWNER TO postgres;

CREATE TABLE public.requests (
    request_id integer NOT NULL,
    ride_id integer,
    requester_id character varying(20),
    request_status_id integer
);


ALTER TABLE public.requests OWNER TO postgres;

CREATE TABLE public.rides (
    ride_id integer NOT NULL,
    member_car_id integer,
    departure_date date,
    departure_time character varying(5),
    starting_city_id integer,
    destination_city_id integer,
    number_seats integer,
    contribution_per_passenger numeric(8,2),
    luggage_id integer
);

ALTER TABLE public.rides OWNER TO postgres;

ALTER TABLE ONLY public.cars
    ADD CONSTRAINT cars_pkey PRIMARY KEY (car_id);

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_pkey PRIMARY KEY (city_id);

ALTER TABLE ONLY public.luggage_types
    ADD CONSTRAINT luggage_types_pkey PRIMARY KEY (luggage_type_id);

ALTER TABLE ONLY public.member_car
    ADD CONSTRAINT member_car_pkey PRIMARY KEY (member_car_id);

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_pkey PRIMARY KEY (member_id);

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (message_id);

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_pkey PRIMARY KEY (rating_id);

ALTER TABLE ONLY public.request_status
    ADD CONSTRAINT request_status_pkey PRIMARY KEY (request_status_id);

ALTER TABLE ONLY public.requests
    ADD CONSTRAINT requests_pkey PRIMARY KEY (request_id);

ALTER TABLE ONLY public.rides
    ADD CONSTRAINT rides_pkey PRIMARY KEY (ride_id);

ALTER TABLE ONLY public.member_car
    ADD CONSTRAINT member_car_car_id_fkey FOREIGN KEY (car_id) REFERENCES public.cars(car_id);

ALTER TABLE ONLY public.member_car
    ADD CONSTRAINT member_car_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(member_id);

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.members(member_id);

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.members(member_id);

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_rating_giver_id_fkey FOREIGN KEY (rating_giver_id) REFERENCES public.members(member_id);

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_rating_receiver_id_fkey FOREIGN KEY (rating_receiver_id) REFERENCES public.members(member_id);

ALTER TABLE ONLY public.requests
    ADD CONSTRAINT requests_request_status_id_fkey FOREIGN KEY (request_status_id) REFERENCES public.request_status(request_status_id);

ALTER TABLE ONLY public.requests
    ADD CONSTRAINT requests_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.members(member_id);

ALTER TABLE ONLY public.requests
    ADD CONSTRAINT requests_ride_id_fkey FOREIGN KEY (ride_id) REFERENCES public.rides(ride_id);

ALTER TABLE ONLY public.rides
    ADD CONSTRAINT rides_destination_city_id_fkey FOREIGN KEY (destination_city_id) REFERENCES public.cities(city_id);

ALTER TABLE ONLY public.rides
    ADD CONSTRAINT rides_luggage_id_fkey FOREIGN KEY (luggage_id) REFERENCES public.luggage_types(luggage_type_id);

ALTER TABLE ONLY public.rides
    ADD CONSTRAINT rides_member_car_id_fkey FOREIGN KEY (member_car_id) REFERENCES public.member_car(member_car_id);

ALTER TABLE ONLY public.rides
    ADD CONSTRAINT rides_starting_city_id_fkey FOREIGN KEY (starting_city_id) REFERENCES public.cities(city_id);
