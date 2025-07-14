--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: module; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.module AS ENUM (
    'EMPLOYEES',
    'ATTENDANCE',
    'DEPARTMENTS',
    'SALARIES',
    'DOCUMENTS',
    'VEHICLES',
    'USERS',
    'REPORTS',
    'FEES'
);


ALTER TYPE public.module OWNER TO neondb_owner;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'MANAGER',
    'HR',
    'FINANCE',
    'FLEET',
    'USER'
);


ALTER TYPE public.userrole OWNER TO neondb_owner;

--
-- Name: usertype; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.usertype AS ENUM (
    'SYSTEM_ADMIN',
    'COMPANY_ADMIN',
    'EMPLOYEE'
);


ALTER TYPE public.usertype OWNER TO neondb_owner;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: attendance; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.attendance (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    date date NOT NULL,
    check_in time without time zone,
    check_out time without time zone,
    status character varying(20) NOT NULL,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    company_id integer
);


ALTER TABLE public.attendance OWNER TO neondb_owner;

--
-- Name: attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendance_id_seq OWNER TO neondb_owner;

--
-- Name: attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.attendance_id_seq OWNED BY public.attendance.id;


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    user_id integer NOT NULL,
    action character varying(50) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id integer,
    details text,
    ip_address character varying(45),
    user_agent text,
    previous_data text,
    new_data text,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.audit_log OWNER TO neondb_owner;

--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_log_id_seq OWNER TO neondb_owner;

--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.companies (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    contact_email character varying(100),
    contact_phone character varying(20),
    address text,
    status character varying(20),
    is_trial boolean,
    trial_start_date date,
    trial_end_date date,
    trial_days integer,
    trial_extended boolean,
    subscription_start_date date,
    subscription_end_date date,
    subscription_status character varying(20),
    subscription_plan character varying(50),
    max_users integer,
    max_employees integer,
    max_vehicles integer,
    max_departments integer,
    monthly_fee double precision,
    last_payment_date date,
    next_payment_due date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.companies OWNER TO neondb_owner;

--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companies_id_seq OWNER TO neondb_owner;

--
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- Name: company_permissions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.company_permissions (
    id integer NOT NULL,
    company_id integer NOT NULL,
    module_name character varying(50) NOT NULL,
    permissions text,
    is_enabled boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.company_permissions OWNER TO neondb_owner;

--
-- Name: company_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.company_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_permissions_id_seq OWNER TO neondb_owner;

--
-- Name: company_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.company_permissions_id_seq OWNED BY public.company_permissions.id;


--
-- Name: company_subscriptions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.company_subscriptions (
    id integer NOT NULL,
    company_id integer NOT NULL,
    plan_type character varying(20) NOT NULL,
    is_trial boolean,
    trial_start_date timestamp without time zone,
    trial_end_date timestamp without time zone,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    is_active boolean,
    auto_renew boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.company_subscriptions OWNER TO neondb_owner;

--
-- Name: company_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.company_subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_subscriptions_id_seq OWNER TO neondb_owner;

--
-- Name: company_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.company_subscriptions_id_seq OWNED BY public.company_subscriptions.id;


--
-- Name: department; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.department (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    manager_id integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    company_id integer
);


ALTER TABLE public.department OWNER TO neondb_owner;

--
-- Name: department_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.department_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.department_id_seq OWNER TO neondb_owner;

--
-- Name: department_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.department_id_seq OWNED BY public.department.id;


--
-- Name: document; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.document (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    document_type character varying(50) NOT NULL,
    document_number character varying(100) NOT NULL,
    issue_date date,
    expiry_date date,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.document OWNER TO neondb_owner;

--
-- Name: document_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.document_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.document_id_seq OWNER TO neondb_owner;

--
-- Name: document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.document_id_seq OWNED BY public.document.id;


--
-- Name: employee; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.employee (
    id integer NOT NULL,
    employee_id character varying(20) NOT NULL,
    national_id character varying(20) NOT NULL,
    name character varying(100) NOT NULL,
    mobile character varying(20) NOT NULL,
    email character varying(100),
    job_title character varying(100) NOT NULL,
    status character varying(20) NOT NULL,
    location character varying(100),
    project character varying(100),
    department_id integer,
    join_date date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    nationality character varying(50),
    contract_type character varying(20) DEFAULT 'foreign'::character varying,
    basic_salary double precision DEFAULT 0.0,
    has_national_balance boolean DEFAULT false,
    profile_image character varying(255),
    national_id_image character varying(255),
    license_image character varying(255),
    company_id integer,
    "mobilePersonal" character varying(20),
    nationality_id integer,
    contract_status character varying(20),
    license_status character varying(20)
);


ALTER TABLE public.employee OWNER TO neondb_owner;

--
-- Name: employee_departments; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.employee_departments (
    employee_id integer NOT NULL,
    department_id integer NOT NULL
);


ALTER TABLE public.employee_departments OWNER TO neondb_owner;

--
-- Name: employee_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.employee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_id_seq OWNER TO neondb_owner;

--
-- Name: employee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.employee_id_seq OWNED BY public.employee.id;


--
-- Name: external_authorization; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.external_authorization (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    employee_id integer NOT NULL,
    project_id integer,
    authorization_type character varying(100) NOT NULL,
    status character varying(20),
    file_path character varying(255),
    external_link character varying(500),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    project_name character varying(200),
    city character varying(100)
);


ALTER TABLE public.external_authorization OWNER TO neondb_owner;

--
-- Name: external_authorization_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.external_authorization_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.external_authorization_id_seq OWNER TO neondb_owner;

--
-- Name: external_authorization_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.external_authorization_id_seq OWNED BY public.external_authorization.id;


--
-- Name: external_authorizations; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.external_authorizations (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    driver_name character varying(100) NOT NULL,
    driver_phone character varying(20),
    project_name character varying(200) NOT NULL,
    city character varying(100) NOT NULL,
    authorization_type character varying(50) NOT NULL,
    duration character varying(100),
    authorization_form_link character varying(500),
    external_reference character varying(100),
    file_path character varying(255),
    notes text,
    status character varying(20),
    created_by integer,
    approved_by integer,
    approved_date timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.external_authorizations OWNER TO neondb_owner;

--
-- Name: external_authorizations_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.external_authorizations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.external_authorizations_id_seq OWNER TO neondb_owner;

--
-- Name: external_authorizations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.external_authorizations_id_seq OWNED BY public.external_authorizations.id;


--
-- Name: fee; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.fee (
    id integer NOT NULL,
    fee_type character varying(50) NOT NULL,
    description character varying(255),
    amount double precision NOT NULL,
    due_date date,
    is_paid boolean,
    paid_date date,
    recipient character varying(100),
    reference_number character varying(50),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    employee_id integer,
    document_id integer,
    vehicle_id integer
);


ALTER TABLE public.fee OWNER TO neondb_owner;

--
-- Name: fee_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.fee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fee_id_seq OWNER TO neondb_owner;

--
-- Name: fee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.fee_id_seq OWNED BY public.fee.id;


--
-- Name: fees_cost; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.fees_cost (
    id integer NOT NULL,
    document_id integer NOT NULL,
    document_type character varying(50) NOT NULL,
    passport_fee double precision,
    labor_office_fee double precision,
    insurance_fee double precision,
    social_insurance_fee double precision,
    transfer_sponsorship boolean,
    due_date date NOT NULL,
    payment_status character varying(20),
    payment_date date,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.fees_cost OWNER TO neondb_owner;

--
-- Name: fees_cost_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.fees_cost_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fees_cost_id_seq OWNER TO neondb_owner;

--
-- Name: fees_cost_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.fees_cost_id_seq OWNED BY public.fees_cost.id;


--
-- Name: government_fee; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.government_fee (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    fee_type character varying(50) NOT NULL,
    fee_date date NOT NULL,
    due_date date NOT NULL,
    amount double precision NOT NULL,
    payment_status character varying(20),
    payment_date date,
    is_automatic boolean,
    insurance_level character varying(20),
    has_national_balance boolean,
    receipt_number character varying(50),
    document_id integer,
    transfer_number character varying(50),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.government_fee OWNER TO neondb_owner;

--
-- Name: government_fee_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.government_fee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.government_fee_id_seq OWNER TO neondb_owner;

--
-- Name: government_fee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.government_fee_id_seq OWNED BY public.government_fee.id;


--
-- Name: nationalities; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.nationalities (
    id integer NOT NULL,
    name_ar character varying(100) NOT NULL,
    name_en character varying(100),
    country_code character varying(3)
);


ALTER TABLE public.nationalities OWNER TO neondb_owner;

--
-- Name: nationalities_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.nationalities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nationalities_id_seq OWNER TO neondb_owner;

--
-- Name: nationalities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.nationalities_id_seq OWNED BY public.nationalities.id;


--
-- Name: project; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.project (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone
);


ALTER TABLE public.project OWNER TO neondb_owner;

--
-- Name: project_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.project_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_id_seq OWNER TO neondb_owner;

--
-- Name: project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.project_id_seq OWNED BY public.project.id;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.projects (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    location character varying(100),
    start_date date,
    end_date date,
    status character varying(20),
    manager_id integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.projects OWNER TO neondb_owner;

--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.projects_id_seq OWNER TO neondb_owner;

--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- Name: renewal_fee; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.renewal_fee (
    id integer NOT NULL,
    document_id integer NOT NULL,
    fee_date date NOT NULL,
    fee_type character varying(50) NOT NULL,
    amount double precision NOT NULL,
    payment_status character varying(20),
    payment_date date,
    receipt_number character varying(50),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    transfer_number character varying(50)
);


ALTER TABLE public.renewal_fee OWNER TO neondb_owner;

--
-- Name: renewal_fee_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.renewal_fee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.renewal_fee_id_seq OWNER TO neondb_owner;

--
-- Name: renewal_fee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.renewal_fee_id_seq OWNED BY public.renewal_fee.id;


--
-- Name: salary; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.salary (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    month integer NOT NULL,
    year integer NOT NULL,
    basic_salary double precision NOT NULL,
    allowances double precision,
    deductions double precision,
    bonus double precision,
    net_salary double precision NOT NULL,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    company_id integer
);


ALTER TABLE public.salary OWNER TO neondb_owner;

--
-- Name: salary_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.salary_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.salary_id_seq OWNER TO neondb_owner;

--
-- Name: salary_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.salary_id_seq OWNED BY public.salary.id;


--
-- Name: subscription_notifications; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.subscription_notifications (
    id integer NOT NULL,
    company_id integer NOT NULL,
    notification_type character varying(50) NOT NULL,
    title character varying(200) NOT NULL,
    message text NOT NULL,
    is_read boolean,
    is_urgent boolean,
    sent_date timestamp without time zone,
    expires_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.subscription_notifications OWNER TO neondb_owner;

--
-- Name: subscription_notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.subscription_notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscription_notifications_id_seq OWNER TO neondb_owner;

--
-- Name: subscription_notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.subscription_notifications_id_seq OWNED BY public.subscription_notifications.id;


--
-- Name: system_audit; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.system_audit (
    id integer NOT NULL,
    action character varying(100) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id integer NOT NULL,
    entity_name character varying(255),
    previous_data text,
    new_data text,
    details text,
    ip_address character varying(50),
    "timestamp" timestamp without time zone,
    user_id integer
);


ALTER TABLE public.system_audit OWNER TO neondb_owner;

--
-- Name: system_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.system_audit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_audit_id_seq OWNER TO neondb_owner;

--
-- Name: system_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.system_audit_id_seq OWNED BY public.system_audit.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    email character varying(100) NOT NULL,
    name character varying(100),
    firebase_uid character varying(128),
    password_hash character varying(256),
    profile_picture character varying(255),
    role public.userrole,
    created_at timestamp without time zone,
    last_login timestamp without time zone,
    is_active boolean,
    auth_type character varying(20),
    employee_id integer,
    assigned_department_id integer,
    company_id integer,
    user_type public.usertype DEFAULT 'EMPLOYEE'::public.usertype,
    parent_user_id integer,
    created_by integer
);


ALTER TABLE public."user" OWNER TO neondb_owner;

--
-- Name: user_accessible_departments; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.user_accessible_departments (
    user_id integer NOT NULL,
    department_id integer NOT NULL
);


ALTER TABLE public.user_accessible_departments OWNER TO neondb_owner;

--
-- Name: user_department_access; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.user_department_access (
    id integer NOT NULL,
    user_id integer NOT NULL,
    department_id integer NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.user_department_access OWNER TO neondb_owner;

--
-- Name: user_department_access_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.user_department_access_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_department_access_id_seq OWNER TO neondb_owner;

--
-- Name: user_department_access_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.user_department_access_id_seq OWNED BY public.user_department_access.id;


--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO neondb_owner;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: user_permission; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.user_permission (
    id integer NOT NULL,
    user_id integer NOT NULL,
    module public.module NOT NULL,
    permissions integer
);


ALTER TABLE public.user_permission OWNER TO neondb_owner;

--
-- Name: user_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.user_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_permission_id_seq OWNER TO neondb_owner;

--
-- Name: user_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.user_permission_id_seq OWNED BY public.user_permission.id;


--
-- Name: vehicle; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle (
    id integer NOT NULL,
    plate_number character varying(20) NOT NULL,
    make character varying(50) NOT NULL,
    model character varying(50) NOT NULL,
    year integer NOT NULL,
    color character varying(30) NOT NULL,
    status character varying(30) NOT NULL,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    authorization_expiry_date date,
    registration_expiry_date date,
    inspection_expiry_date date,
    driver_name character varying(100),
    company_id integer
);


ALTER TABLE public.vehicle OWNER TO neondb_owner;

--
-- Name: vehicle_accident; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_accident (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    accident_date date NOT NULL,
    driver_name character varying(100) NOT NULL,
    accident_status character varying(50),
    vehicle_condition character varying(100),
    deduction_amount double precision,
    deduction_status boolean,
    accident_file_link character varying(255),
    location character varying(255),
    description text,
    police_report boolean,
    insurance_claim boolean,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    liability_percentage integer DEFAULT 0
);


ALTER TABLE public.vehicle_accident OWNER TO neondb_owner;

--
-- Name: vehicle_accident_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_accident_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_accident_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_accident_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_accident_id_seq OWNED BY public.vehicle_accident.id;


--
-- Name: vehicle_checklist; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_checklist (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    inspection_date date NOT NULL,
    inspector_name character varying(100) NOT NULL,
    inspection_type character varying(20) NOT NULL,
    status character varying(20),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.vehicle_checklist OWNER TO neondb_owner;

--
-- Name: vehicle_checklist_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_checklist_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_checklist_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_checklist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_checklist_id_seq OWNED BY public.vehicle_checklist.id;


--
-- Name: vehicle_checklist_image; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_checklist_image (
    id integer NOT NULL,
    checklist_id integer NOT NULL,
    image_path character varying(255) NOT NULL,
    image_type character varying(50),
    description text,
    created_at timestamp without time zone
);


ALTER TABLE public.vehicle_checklist_image OWNER TO neondb_owner;

--
-- Name: vehicle_checklist_image_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_checklist_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_checklist_image_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_checklist_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_checklist_image_id_seq OWNED BY public.vehicle_checklist_image.id;


--
-- Name: vehicle_checklist_item; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_checklist_item (
    id integer NOT NULL,
    checklist_id integer NOT NULL,
    category character varying(50) NOT NULL,
    item_name character varying(100) NOT NULL,
    status character varying(20) NOT NULL,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.vehicle_checklist_item OWNER TO neondb_owner;

--
-- Name: vehicle_checklist_item_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_checklist_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_checklist_item_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_checklist_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_checklist_item_id_seq OWNED BY public.vehicle_checklist_item.id;


--
-- Name: vehicle_damage_marker; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_damage_marker (
    id integer NOT NULL,
    checklist_id integer NOT NULL,
    marker_type character varying(20) NOT NULL,
    position_x double precision NOT NULL,
    position_y double precision NOT NULL,
    color character varying(20),
    size double precision,
    notes text,
    created_at timestamp without time zone
);


ALTER TABLE public.vehicle_damage_marker OWNER TO neondb_owner;

--
-- Name: vehicle_damage_marker_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_damage_marker_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_damage_marker_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_damage_marker_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_damage_marker_id_seq OWNED BY public.vehicle_damage_marker.id;


--
-- Name: vehicle_fuel_consumption; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_fuel_consumption (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    date date NOT NULL,
    liters double precision NOT NULL,
    cost double precision NOT NULL,
    kilometer_reading integer,
    driver_name character varying(100),
    fuel_type character varying(20),
    filling_station character varying(100),
    notes text,
    created_at timestamp without time zone
);


ALTER TABLE public.vehicle_fuel_consumption OWNER TO neondb_owner;

--
-- Name: vehicle_fuel_consumption_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_fuel_consumption_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_fuel_consumption_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_fuel_consumption_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_fuel_consumption_id_seq OWNED BY public.vehicle_fuel_consumption.id;


--
-- Name: vehicle_handover; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_handover (
    id integer NOT NULL,
    handover_type character varying(20) NOT NULL,
    handover_date date NOT NULL,
    mileage integer NOT NULL,
    handover_time time without time zone,
    project_name character varying(100),
    city character varying(100),
    vehicle_id integer NOT NULL,
    employee_id integer,
    supervisor_employee_id integer,
    vehicle_car_type character varying(100),
    vehicle_plate_number character varying(20),
    vehicle_model_year character varying(10),
    person_name character varying(100) NOT NULL,
    driver_company_id character varying(50),
    driver_phone_number character varying(20),
    driver_residency_number character varying(50),
    driver_contract_status character varying(50),
    driver_license_status character varying(50),
    driver_signature_path character varying(255),
    supervisor_name character varying(100),
    supervisor_company_id character varying(50),
    supervisor_phone_number character varying(20),
    supervisor_residency_number character varying(50),
    supervisor_contract_status character varying(50),
    supervisor_license_status character varying(50),
    supervisor_signature_path character varying(255),
    reason_for_change text,
    vehicle_status_summary text,
    notes text,
    reason_for_authorization text,
    authorization_details text,
    fuel_level character varying(50),
    has_spare_tire boolean DEFAULT false,
    has_fire_extinguisher boolean DEFAULT false,
    has_first_aid_kit boolean DEFAULT false,
    has_warning_triangle boolean DEFAULT false,
    has_tools boolean DEFAULT false,
    has_oil_leaks boolean DEFAULT false,
    has_gear_issue boolean DEFAULT false,
    has_clutch_issue boolean DEFAULT false,
    has_engine_issue boolean DEFAULT false,
    has_windows_issue boolean DEFAULT false,
    has_tires_issue boolean DEFAULT false,
    has_body_issue boolean DEFAULT false,
    has_electricity_issue boolean DEFAULT false,
    has_lights_issue boolean DEFAULT false,
    has_ac_issue boolean DEFAULT false,
    movement_officer_name character varying(255),
    movement_officer_signature_path character varying(255),
    damage_diagram_path character varying(255),
    form_link character varying(255),
    custom_company_name character varying(255),
    custom_logo_path character varying(255),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.vehicle_handover OWNER TO neondb_owner;

--
-- Name: vehicle_handover_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_handover_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_handover_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_handover_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_handover_id_seq OWNED BY public.vehicle_handover.id;


--
-- Name: vehicle_handover_image; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_handover_image (
    id integer NOT NULL,
    handover_record_id integer NOT NULL,
    image_path character varying(255) NOT NULL,
    image_description character varying(100),
    uploaded_at timestamp without time zone,
    file_path character varying(255),
    file_type character varying(20) DEFAULT 'image'::character varying,
    file_description character varying(200)
);


ALTER TABLE public.vehicle_handover_image OWNER TO neondb_owner;

--
-- Name: vehicle_handover_image_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_handover_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_handover_image_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_handover_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_handover_image_id_seq OWNED BY public.vehicle_handover_image.id;


--
-- Name: vehicle_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_id_seq OWNED BY public.vehicle.id;


--
-- Name: vehicle_maintenance; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_maintenance (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    date date NOT NULL,
    maintenance_type character varying(30) NOT NULL,
    description character varying(200) NOT NULL,
    status character varying(20) NOT NULL,
    cost double precision,
    technician character varying(100) NOT NULL,
    parts_replaced text,
    actions_taken text,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    receipt_image_url character varying(255),
    delivery_receipt_url character varying(255),
    pickup_receipt_url character varying(255)
);


ALTER TABLE public.vehicle_maintenance OWNER TO neondb_owner;

--
-- Name: vehicle_maintenance_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_maintenance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_maintenance_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_maintenance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_maintenance_id_seq OWNED BY public.vehicle_maintenance.id;


--
-- Name: vehicle_maintenance_image; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_maintenance_image (
    id integer NOT NULL,
    maintenance_id integer NOT NULL,
    image_path character varying(255) NOT NULL,
    image_type character varying(20) NOT NULL,
    uploaded_at timestamp without time zone
);


ALTER TABLE public.vehicle_maintenance_image OWNER TO neondb_owner;

--
-- Name: vehicle_maintenance_image_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_maintenance_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_maintenance_image_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_maintenance_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_maintenance_image_id_seq OWNED BY public.vehicle_maintenance_image.id;


--
-- Name: vehicle_periodic_inspection; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_periodic_inspection (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    inspection_date date NOT NULL,
    expiry_date date NOT NULL,
    inspection_number character varying(50),
    inspector_name character varying(100),
    inspection_type character varying(50),
    inspection_status character varying(20),
    cost double precision,
    results text,
    recommendations text,
    certificate_file character varying(255),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    inspection_center character varying(100),
    result character varying(100),
    driver_name character varying(100),
    supervisor_name character varying(100)
);


ALTER TABLE public.vehicle_periodic_inspection OWNER TO neondb_owner;

--
-- Name: vehicle_periodic_inspection_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_periodic_inspection_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_periodic_inspection_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_periodic_inspection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_periodic_inspection_id_seq OWNED BY public.vehicle_periodic_inspection.id;


--
-- Name: vehicle_project; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_project (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    project_name character varying(100) NOT NULL,
    location character varying(100) NOT NULL,
    manager_name character varying(100) NOT NULL,
    start_date date NOT NULL,
    end_date date,
    is_active boolean,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.vehicle_project OWNER TO neondb_owner;

--
-- Name: vehicle_project_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_project_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_project_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_project_id_seq OWNED BY public.vehicle_project.id;


--
-- Name: vehicle_rental; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_rental (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date,
    monthly_cost double precision NOT NULL,
    is_active boolean,
    lessor_name character varying(100),
    lessor_contact character varying(100),
    contract_number character varying(50),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    city character varying(100),
    company_id integer
);


ALTER TABLE public.vehicle_rental OWNER TO neondb_owner;

--
-- Name: vehicle_rental_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_rental_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_rental_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_rental_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_rental_id_seq OWNED BY public.vehicle_rental.id;


--
-- Name: vehicle_safety_check; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_safety_check (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    check_date date NOT NULL,
    check_type character varying(20) NOT NULL,
    driver_id integer,
    driver_name character varying(100) NOT NULL,
    supervisor_id integer,
    supervisor_name character varying(100) NOT NULL,
    status character varying(20),
    check_form_link character varying(255),
    issues_found boolean,
    issues_description text,
    actions_taken text,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.vehicle_safety_check OWNER TO neondb_owner;

--
-- Name: vehicle_safety_check_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_safety_check_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_safety_check_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_safety_check_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_safety_check_id_seq OWNED BY public.vehicle_safety_check.id;


--
-- Name: vehicle_workshop; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_workshop (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    entry_date date NOT NULL,
    exit_date date,
    reason character varying(50) NOT NULL,
    description text NOT NULL,
    repair_status character varying(30) NOT NULL,
    cost double precision,
    workshop_name character varying(100),
    technician_name character varying(100),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    delivery_link character varying(255),
    reception_link character varying(255),
    status character varying(20) DEFAULT 'in_progress'::character varying
);


ALTER TABLE public.vehicle_workshop OWNER TO neondb_owner;

--
-- Name: vehicle_workshop_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_workshop_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_workshop_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_workshop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_workshop_id_seq OWNED BY public.vehicle_workshop.id;


--
-- Name: vehicle_workshop_image; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicle_workshop_image (
    id integer NOT NULL,
    workshop_record_id integer NOT NULL,
    image_type character varying(20) NOT NULL,
    image_path character varying(255) NOT NULL,
    uploaded_at timestamp without time zone,
    notes text
);


ALTER TABLE public.vehicle_workshop_image OWNER TO neondb_owner;

--
-- Name: vehicle_workshop_image_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicle_workshop_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_workshop_image_id_seq OWNER TO neondb_owner;

--
-- Name: vehicle_workshop_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicle_workshop_image_id_seq OWNED BY public.vehicle_workshop_image.id;


--
-- Name: vehicles; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vehicles (
    id integer NOT NULL,
    plate_number character varying(20) NOT NULL,
    make character varying(50),
    model character varying(50),
    year integer,
    color character varying(30),
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.vehicles OWNER TO neondb_owner;

--
-- Name: vehicles_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.vehicles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicles_id_seq OWNER TO neondb_owner;

--
-- Name: vehicles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.vehicles_id_seq OWNED BY public.vehicles.id;


--
-- Name: attendance id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attendance ALTER COLUMN id SET DEFAULT nextval('public.attendance_id_seq'::regclass);


--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- Name: company_permissions id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.company_permissions ALTER COLUMN id SET DEFAULT nextval('public.company_permissions_id_seq'::regclass);


--
-- Name: company_subscriptions id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.company_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.company_subscriptions_id_seq'::regclass);


--
-- Name: department id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.department ALTER COLUMN id SET DEFAULT nextval('public.department_id_seq'::regclass);


--
-- Name: document id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.document ALTER COLUMN id SET DEFAULT nextval('public.document_id_seq'::regclass);


--
-- Name: employee id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.employee ALTER COLUMN id SET DEFAULT nextval('public.employee_id_seq'::regclass);


--
-- Name: external_authorization id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.external_authorization ALTER COLUMN id SET DEFAULT nextval('public.external_authorization_id_seq'::regclass);


--
-- Name: external_authorizations id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.external_authorizations ALTER COLUMN id SET DEFAULT nextval('public.external_authorizations_id_seq'::regclass);


--
-- Name: fee id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.fee ALTER COLUMN id SET DEFAULT nextval('public.fee_id_seq'::regclass);


--
-- Name: fees_cost id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.fees_cost ALTER COLUMN id SET DEFAULT nextval('public.fees_cost_id_seq'::regclass);


--
-- Name: government_fee id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.government_fee ALTER COLUMN id SET DEFAULT nextval('public.government_fee_id_seq'::regclass);


--
-- Name: nationalities id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.nationalities ALTER COLUMN id SET DEFAULT nextval('public.nationalities_id_seq'::regclass);


--
-- Name: project id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.project ALTER COLUMN id SET DEFAULT nextval('public.project_id_seq'::regclass);


--
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- Name: renewal_fee id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.renewal_fee ALTER COLUMN id SET DEFAULT nextval('public.renewal_fee_id_seq'::regclass);


--
-- Name: salary id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.salary ALTER COLUMN id SET DEFAULT nextval('public.salary_id_seq'::regclass);


--
-- Name: subscription_notifications id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.subscription_notifications ALTER COLUMN id SET DEFAULT nextval('public.subscription_notifications_id_seq'::regclass);


--
-- Name: system_audit id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.system_audit ALTER COLUMN id SET DEFAULT nextval('public.system_audit_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: user_department_access id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_department_access ALTER COLUMN id SET DEFAULT nextval('public.user_department_access_id_seq'::regclass);


--
-- Name: user_permission id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_permission ALTER COLUMN id SET DEFAULT nextval('public.user_permission_id_seq'::regclass);


--
-- Name: vehicle id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle ALTER COLUMN id SET DEFAULT nextval('public.vehicle_id_seq'::regclass);


--
-- Name: vehicle_accident id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_accident ALTER COLUMN id SET DEFAULT nextval('public.vehicle_accident_id_seq'::regclass);


--
-- Name: vehicle_checklist id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_checklist ALTER COLUMN id SET DEFAULT nextval('public.vehicle_checklist_id_seq'::regclass);


--
-- Name: vehicle_checklist_image id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_checklist_image ALTER COLUMN id SET DEFAULT nextval('public.vehicle_checklist_image_id_seq'::regclass);


--
-- Name: vehicle_checklist_item id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_checklist_item ALTER COLUMN id SET DEFAULT nextval('public.vehicle_checklist_item_id_seq'::regclass);


--
-- Name: vehicle_damage_marker id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_damage_marker ALTER COLUMN id SET DEFAULT nextval('public.vehicle_damage_marker_id_seq'::regclass);


--
-- Name: vehicle_fuel_consumption id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_fuel_consumption ALTER COLUMN id SET DEFAULT nextval('public.vehicle_fuel_consumption_id_seq'::regclass);


--
-- Name: vehicle_handover id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_handover ALTER COLUMN id SET DEFAULT nextval('public.vehicle_handover_id_seq'::regclass);


--
-- Name: vehicle_handover_image id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_handover_image ALTER COLUMN id SET DEFAULT nextval('public.vehicle_handover_image_id_seq'::regclass);


--
-- Name: vehicle_maintenance id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_maintenance ALTER COLUMN id SET DEFAULT nextval('public.vehicle_maintenance_id_seq'::regclass);


--
-- Name: vehicle_maintenance_image id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_maintenance_image ALTER COLUMN id SET DEFAULT nextval('public.vehicle_maintenance_image_id_seq'::regclass);


--
-- Name: vehicle_periodic_inspection id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_periodic_inspection ALTER COLUMN id SET DEFAULT nextval('public.vehicle_periodic_inspection_id_seq'::regclass);


--
-- Name: vehicle_project id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_project ALTER COLUMN id SET DEFAULT nextval('public.vehicle_project_id_seq'::regclass);


--
-- Name: vehicle_rental id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_rental ALTER COLUMN id SET DEFAULT nextval('public.vehicle_rental_id_seq'::regclass);


--
-- Name: vehicle_safety_check id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_safety_check ALTER COLUMN id SET DEFAULT nextval('public.vehicle_safety_check_id_seq'::regclass);


--
-- Name: vehicle_workshop id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_workshop ALTER COLUMN id SET DEFAULT nextval('public.vehicle_workshop_id_seq'::regclass);


--
-- Name: vehicle_workshop_image id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_workshop_image ALTER COLUMN id SET DEFAULT nextval('public.vehicle_workshop_image_id_seq'::regclass);


--
-- Name: vehicles id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicles ALTER COLUMN id SET DEFAULT nextval('public.vehicles_id_seq'::regclass);


--
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.attendance (id, employee_id, date, check_in, check_out, status, notes, created_at, updated_at, company_id) FROM stdin;
460	180	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:45.610054	2025-04-21 19:31:45.610058	1
6829	184	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:50.199352	2025-06-20 23:40:50.199356	\N
6830	185	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:50.309387	2025-06-20 23:40:50.309392	\N
6831	186	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:50.404551	2025-06-20 23:40:50.404555	\N
461	181	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:45.694193	2025-04-21 19:31:45.694197	1
6832	187	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:50.493684	2025-06-20 23:40:50.493688	\N
6833	188	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:50.583675	2025-06-20 23:40:50.58368	\N
6834	184	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:50.674526	2025-06-20 23:40:50.67453	\N
6835	185	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:50.76871	2025-06-20 23:40:50.768715	\N
6836	186	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:50.860074	2025-06-20 23:40:50.860078	\N
6837	187	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:50.948402	2025-06-20 23:40:50.948406	\N
6838	188	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:51.037486	2025-06-20 23:40:51.037488	\N
6884	193	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:59.569659	2025-06-20 23:40:59.569663	\N
6885	190	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:59.657761	2025-06-20 23:40:59.657766	\N
6886	192	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:59.745979	2025-06-20 23:40:59.745983	\N
6887	191	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:59.83402	2025-06-20 23:40:59.834024	\N
6888	189	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:59.929922	2025-06-20 23:40:59.929926	\N
6889	193	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:00.01794	2025-06-20 23:41:00.017945	\N
6890	190	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:00.107031	2025-06-20 23:41:00.107036	\N
6891	192	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:00.195823	2025-06-20 23:41:00.195827	\N
6892	191	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:00.283996	2025-06-20 23:41:00.284	\N
462	179	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:45.778395	2025-04-21 19:31:45.778399	1
6893	189	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:00.371967	2025-06-20 23:41:00.37197	\N
6932	216	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:10.313252	2025-06-20 23:41:10.313257	\N
6933	217	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:10.403354	2025-06-20 23:41:10.403359	\N
6934	218	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:10.492334	2025-06-20 23:41:10.492338	\N
6935	219	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:10.581064	2025-06-20 23:41:10.581069	\N
6936	220	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:10.669456	2025-06-20 23:41:10.66946	\N
6937	221	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:10.818494	2025-06-20 23:41:10.818499	\N
6938	222	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:10.907061	2025-06-20 23:41:10.907066	\N
6939	216	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:10.994985	2025-06-20 23:41:10.99499	\N
6940	217	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:11.083372	2025-06-20 23:41:11.083376	\N
6941	218	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:11.171623	2025-06-20 23:41:11.171627	\N
6942	219	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:11.260461	2025-06-20 23:41:11.260465	\N
6943	220	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:11.349047	2025-06-20 23:41:11.349051	\N
6944	221	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:11.437488	2025-06-20 23:41:11.437492	\N
6945	222	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:11.525646	2025-06-20 23:41:11.525649	\N
6950	184	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:06.808114	2025-06-21 09:38:06.808118	\N
463	178	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:45.863581	2025-04-21 19:31:45.863605	1
6951	185	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:06.912831	2025-06-21 09:38:06.912835	\N
6952	186	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:07.00064	2025-06-21 09:38:07.000645	\N
6953	187	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:07.088795	2025-06-21 09:38:07.088799	\N
6954	188	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:07.17642	2025-06-21 09:38:07.176424	\N
6955	175	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:07.574628	2025-06-21 09:38:07.574633	\N
6956	178	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:07.662585	2025-06-21 09:38:07.66259	\N
6957	180	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:07.751129	2025-06-21 09:38:07.751133	\N
6958	182	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:07.838851	2025-06-21 09:38:07.838857	\N
6959	173	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:07.926513	2025-06-21 09:38:07.926517	\N
6960	172	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:08.013694	2025-06-21 09:38:08.013698	\N
6961	171	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:08.101017	2025-06-21 09:38:08.101022	\N
6962	174	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:08.188424	2025-06-21 09:38:08.188428	\N
6963	177	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:08.275979	2025-06-21 09:38:08.275983	\N
6964	169	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:08.363389	2025-06-21 09:38:08.363394	\N
6965	183	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:08.457091	2025-06-21 09:38:08.457096	\N
6966	181	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:08.544498	2025-06-21 09:38:08.544503	\N
464	183	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:45.947734	2025-04-21 19:31:45.947737	1
6967	179	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:08.633575	2025-06-21 09:38:08.63358	\N
6968	226	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:08.721596	2025-06-21 09:38:08.721601	\N
6969	227	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:08.809224	2025-06-21 09:38:08.809226	\N
6970	193	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:09.202939	2025-06-21 09:38:09.202944	\N
6971	190	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:09.29136	2025-06-21 09:38:09.291364	\N
6972	192	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:09.379127	2025-06-21 09:38:09.379131	\N
6973	191	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:09.466329	2025-06-21 09:38:09.466333	\N
6974	189	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:09.553434	2025-06-21 09:38:09.553436	\N
6975	214	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:09.943656	2025-06-21 09:38:09.94366	\N
6976	194	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.031969	2025-06-21 09:38:10.03198	\N
6977	195	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.122608	2025-06-21 09:38:10.122613	\N
6978	196	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.209992	2025-06-21 09:38:10.209997	\N
6979	197	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.297196	2025-06-21 09:38:10.297201	\N
6980	200	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.385655	2025-06-21 09:38:10.38566	\N
6981	202	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.476777	2025-06-21 09:38:10.476782	\N
6982	203	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.56461	2025-06-21 09:38:10.564658	\N
6983	205	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.653084	2025-06-21 09:38:10.653089	\N
465	182	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:46.032207	2025-04-21 19:31:46.032212	1
6984	206	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.740786	2025-06-21 09:38:10.740791	\N
6985	207	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.828084	2025-06-21 09:38:10.828088	\N
6986	208	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:10.915445	2025-06-21 09:38:10.91545	\N
6987	209	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:11.003785	2025-06-21 09:38:11.003789	\N
6988	198	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:11.09196	2025-06-21 09:38:11.091965	\N
6989	201	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:11.17971	2025-06-21 09:38:11.179714	\N
6990	204	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:11.268902	2025-06-21 09:38:11.268906	\N
6991	225	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:11.356274	2025-06-21 09:38:11.356279	\N
6992	230	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:11.44388	2025-06-21 09:38:11.443885	\N
6993	231	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:11.531449	2025-06-21 09:38:11.531451	\N
6994	216	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:11.926134	2025-06-21 09:38:11.926142	\N
6995	217	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:12.01469	2025-06-21 09:38:12.014694	\N
6996	218	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:12.102233	2025-06-21 09:38:12.102237	\N
6997	219	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:12.190362	2025-06-21 09:38:12.190367	\N
6998	220	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:12.277738	2025-06-21 09:38:12.277743	\N
6999	221	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:12.365846	2025-06-21 09:38:12.365851	\N
7000	222	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:12.453573	2025-06-21 09:38:12.453576	\N
7001	223	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:12.844301	2025-06-21 09:38:12.844307	\N
7002	224	2025-06-21	\N	\N	present	\N	2025-06-21 09:38:12.932419	2025-06-21 09:38:12.932421	\N
7003	184	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:50.181649	2025-06-23 10:35:50.181653	\N
7004	185	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:50.277917	2025-06-23 10:35:50.277922	\N
7005	186	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:50.367034	2025-06-23 10:35:50.367038	\N
7006	187	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:50.455221	2025-06-23 10:35:50.455225	\N
7007	188	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:50.543137	2025-06-23 10:35:50.543139	\N
466	175	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:46.116393	2025-04-21 19:31:46.116396	1
467	173	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:46.20097	2025-04-21 19:31:46.200975	1
468	172	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:46.287133	2025-04-21 19:31:46.287137	1
470	171	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:46.456297	2025-04-21 19:31:46.456301	1
471	174	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:46.541396	2025-04-21 19:31:46.5414	1
472	177	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:46.625843	2025-04-21 19:31:46.625846	1
473	169	2025-04-04	\N	\N	present	\N	2025-04-21 19:31:46.711307	2025-04-21 19:31:46.711311	1
6839	175	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:51.438452	2025-06-20 23:40:51.438456	\N
6840	178	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:51.527124	2025-06-20 23:40:51.527129	\N
6841	180	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:51.615093	2025-06-20 23:40:51.615097	\N
6842	182	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:51.702298	2025-06-20 23:40:51.702303	\N
6843	173	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:51.789564	2025-06-20 23:40:51.789569	\N
6844	172	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:51.876777	2025-06-20 23:40:51.876781	\N
6845	171	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:51.963981	2025-06-20 23:40:51.963985	\N
6846	174	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:52.051243	2025-06-20 23:40:52.051247	\N
6847	177	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:52.139072	2025-06-20 23:40:52.139076	\N
6848	169	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:52.226371	2025-06-20 23:40:52.226376	\N
6849	183	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:52.31351	2025-06-20 23:40:52.313514	\N
6850	181	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:52.402364	2025-06-20 23:40:52.402369	\N
6851	179	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:52.490567	2025-06-20 23:40:52.490572	\N
6852	226	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:52.577721	2025-06-20 23:40:52.577725	\N
6853	227	2025-06-14	\N	\N	present	\N	2025-06-20 23:40:52.666523	2025-06-20 23:40:52.666527	\N
6854	175	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:55.498475	2025-06-20 23:40:55.498479	\N
6855	178	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:55.585737	2025-06-20 23:40:55.585742	\N
6856	180	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:55.673114	2025-06-20 23:40:55.673118	\N
6857	182	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:55.762225	2025-06-20 23:40:55.76223	\N
6858	173	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:55.850586	2025-06-20 23:40:55.85059	\N
6859	172	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:55.938074	2025-06-20 23:40:55.938078	\N
6860	171	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:56.025763	2025-06-20 23:40:56.025768	\N
6861	174	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:56.113158	2025-06-20 23:40:56.113164	\N
6863	169	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:56.288676	2025-06-20 23:40:56.28868	\N
6865	181	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:56.463606	2025-06-20 23:40:56.463611	\N
6866	179	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:56.559652	2025-06-20 23:40:56.559657	\N
6867	226	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:56.646944	2025-06-20 23:40:56.646948	\N
6868	227	2025-06-19	\N	\N	present	\N	2025-06-20 23:40:56.734385	2025-06-20 23:40:56.734389	\N
6869	175	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:56.822358	2025-06-20 23:40:56.822363	\N
6870	178	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:56.909864	2025-06-20 23:40:56.909869	\N
6871	180	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:56.9975	2025-06-20 23:40:56.997504	\N
6872	182	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.085298	2025-06-20 23:40:57.085302	\N
6873	173	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.173392	2025-06-20 23:40:57.173397	\N
6874	172	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.26163	2025-06-20 23:40:57.261635	\N
6875	171	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.350098	2025-06-20 23:40:57.350102	\N
6876	174	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.437761	2025-06-20 23:40:57.437766	\N
6877	177	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.526972	2025-06-20 23:40:57.526976	\N
6878	169	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.615747	2025-06-20 23:40:57.615751	\N
6879	183	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.703791	2025-06-20 23:40:57.703796	\N
6880	181	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.791418	2025-06-20 23:40:57.791423	\N
6881	179	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.8788	2025-06-20 23:40:57.878804	\N
6882	226	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:57.967197	2025-06-20 23:40:57.967202	\N
6883	227	2025-06-20	\N	\N	present	\N	2025-06-20 23:40:58.05629	2025-06-20 23:40:58.056292	\N
6894	214	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.021671	2025-06-20 23:41:05.021676	\N
6895	194	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.108991	2025-06-20 23:41:05.108995	\N
6896	195	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.19617	2025-06-20 23:41:05.196175	\N
6897	196	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.28355	2025-06-20 23:41:05.283554	\N
6898	197	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.37123	2025-06-20 23:41:05.371234	\N
6899	200	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.462642	2025-06-20 23:41:05.462647	\N
6900	202	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.550073	2025-06-20 23:41:05.550077	\N
6901	203	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.637444	2025-06-20 23:41:05.637448	\N
6902	205	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.724578	2025-06-20 23:41:05.724582	\N
6903	206	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.811902	2025-06-20 23:41:05.811906	\N
6904	207	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.899767	2025-06-20 23:41:05.89977	\N
6905	208	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:05.987191	2025-06-20 23:41:05.987195	\N
6906	209	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:06.075853	2025-06-20 23:41:06.075858	\N
6907	198	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:06.163339	2025-06-20 23:41:06.163343	\N
6908	201	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:06.250371	2025-06-20 23:41:06.250376	\N
6909	204	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:06.338119	2025-06-20 23:41:06.338123	\N
6910	225	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:06.425948	2025-06-20 23:41:06.425952	\N
6911	230	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:06.513547	2025-06-20 23:41:06.513552	\N
6912	231	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:06.602969	2025-06-20 23:41:06.602974	\N
6913	214	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:06.6905	2025-06-20 23:41:06.690505	\N
6914	194	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:06.779524	2025-06-20 23:41:06.779528	\N
6915	195	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:06.866876	2025-06-20 23:41:06.86688	\N
6916	196	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:06.956789	2025-06-20 23:41:06.956794	\N
6917	197	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.044098	2025-06-20 23:41:07.044102	\N
6918	200	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.131361	2025-06-20 23:41:07.131365	\N
6919	202	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.218546	2025-06-20 23:41:07.21855	\N
6920	203	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.314603	2025-06-20 23:41:07.314607	\N
6921	205	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.401891	2025-06-20 23:41:07.401895	\N
6922	206	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.489372	2025-06-20 23:41:07.489376	\N
6923	207	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.576518	2025-06-20 23:41:07.576523	\N
6924	208	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.664131	2025-06-20 23:41:07.664136	\N
6925	209	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.751575	2025-06-20 23:41:07.751579	\N
6926	198	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.839486	2025-06-20 23:41:07.83949	\N
6927	201	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:07.926474	2025-06-20 23:41:07.926478	\N
6928	204	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:08.014028	2025-06-20 23:41:08.014032	\N
6929	225	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:08.101465	2025-06-20 23:41:08.101469	\N
6930	230	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:08.189179	2025-06-20 23:41:08.189184	\N
6931	231	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:08.277219	2025-06-20 23:41:08.277221	\N
6946	223	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:12.428347	2025-06-20 23:41:12.428351	\N
6947	224	2025-06-19	\N	\N	present	\N	2025-06-20 23:41:12.515704	2025-06-20 23:41:12.515709	\N
6948	223	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:12.603396	2025-06-20 23:41:12.6034	\N
6949	224	2025-06-20	\N	\N	present	\N	2025-06-20 23:41:12.690711	2025-06-20 23:41:12.690713	\N
7008	175	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:50.950572	2025-06-23 10:35:50.950576	\N
7010	180	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:51.128021	2025-06-23 10:35:51.128025	\N
7012	173	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:51.303113	2025-06-23 10:35:51.303118	\N
7013	172	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:51.390968	2025-06-23 10:35:51.390972	\N
7014	171	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:51.47927	2025-06-23 10:35:51.479274	\N
6864	183	2025-06-19	\N	\N	absent		2025-06-20 23:40:56.37593	2025-06-29 18:36:14.329071	\N
6862	177	2025-06-19	\N	\N	absent		2025-06-20 23:40:56.200887	2025-06-29 18:36:54.33675	\N
569	171	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:42.123744	2025-04-21 23:15:42.123749	1
570	174	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:42.216393	2025-04-21 23:15:42.216397	1
571	177	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:42.307124	2025-04-21 23:15:42.307128	1
572	169	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:42.398244	2025-04-21 23:15:42.398248	1
575	180	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:09.544639	2025-04-21 23:16:09.544644	1
576	181	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:09.638398	2025-04-21 23:16:09.638403	1
577	179	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:09.729232	2025-04-21 23:16:09.729236	1
578	178	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:09.819997	2025-04-21 23:16:09.820001	1
579	183	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:09.917788	2025-04-21 23:16:09.917793	1
580	182	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:10.009496	2025-04-21 23:16:10.009502	1
581	175	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:10.100388	2025-04-21 23:16:10.100393	1
7015	174	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:51.566564	2025-06-23 10:35:51.566569	\N
7022	227	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:52.181991	2025-06-23 10:35:52.181994	\N
7023	193	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:52.590279	2025-06-23 10:35:52.590283	\N
7024	190	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:52.677897	2025-06-23 10:35:52.677901	\N
7025	192	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:52.765491	2025-06-23 10:35:52.765495	\N
7026	191	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:52.852762	2025-06-23 10:35:52.852766	\N
7027	189	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:52.940742	2025-06-23 10:35:52.940745	\N
7028	214	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:53.329812	2025-06-23 10:35:53.329816	\N
7029	194	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:53.417724	2025-06-23 10:35:53.417728	\N
7030	195	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:53.505715	2025-06-23 10:35:53.505719	\N
7031	196	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:53.59307	2025-06-23 10:35:53.593076	\N
7032	197	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:53.680555	2025-06-23 10:35:53.68056	\N
7033	200	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:53.768965	2025-06-23 10:35:53.768969	\N
7034	202	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:53.856756	2025-06-23 10:35:53.85676	\N
7035	203	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:53.944124	2025-06-23 10:35:53.944134	\N
7036	205	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.032305	2025-06-23 10:35:54.032309	\N
7037	206	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.119951	2025-06-23 10:35:54.119956	\N
7038	207	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.207871	2025-06-23 10:35:54.207876	\N
7039	208	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.295179	2025-06-23 10:35:54.295184	\N
7040	209	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.382156	2025-06-23 10:35:54.38216	\N
7041	198	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.473287	2025-06-23 10:35:54.473291	\N
7042	201	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.561925	2025-06-23 10:35:54.56193	\N
7043	204	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.649594	2025-06-23 10:35:54.649598	\N
7044	225	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.737105	2025-06-23 10:35:54.73711	\N
7045	230	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.82498	2025-06-23 10:35:54.824985	\N
7046	231	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:54.912391	2025-06-23 10:35:54.912393	\N
7047	216	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:55.302465	2025-06-23 10:35:55.30247	\N
7048	217	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:55.393672	2025-06-23 10:35:55.393676	\N
7049	218	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:55.481501	2025-06-23 10:35:55.481505	\N
7050	219	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:55.568787	2025-06-23 10:35:55.568792	\N
7051	220	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:55.656399	2025-06-23 10:35:55.656404	\N
7052	221	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:55.744401	2025-06-23 10:35:55.744405	\N
7053	222	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:55.833045	2025-06-23 10:35:55.833047	\N
7054	223	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:56.226626	2025-06-23 10:35:56.22663	\N
7055	224	2025-06-23	\N	\N	present	\N	2025-06-23 10:35:56.313601	2025-06-23 10:35:56.313603	\N
7056	184	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:38.046917	2025-06-23 10:40:38.046922	\N
7057	185	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:38.149009	2025-06-23 10:40:38.149014	\N
7058	186	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:38.236901	2025-06-23 10:40:38.236906	\N
7059	187	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:38.325066	2025-06-23 10:40:38.32507	\N
7060	188	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:38.413302	2025-06-23 10:40:38.413306	\N
7061	175	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:42.480356	2025-06-23 10:40:42.480361	\N
7062	178	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:42.569615	2025-06-23 10:40:42.569619	\N
7063	180	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:42.658616	2025-06-23 10:40:42.65862	\N
7064	182	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:42.746912	2025-06-23 10:40:42.746917	\N
7065	173	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:42.835937	2025-06-23 10:40:42.835941	\N
7066	172	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:42.923837	2025-06-23 10:40:42.923841	\N
7067	171	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:43.011931	2025-06-23 10:40:43.011936	\N
7068	174	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:43.10044	2025-06-23 10:40:43.100444	\N
7069	177	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:43.188692	2025-06-23 10:40:43.188696	\N
7070	169	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:43.278265	2025-06-23 10:40:43.278269	\N
7071	183	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:43.366093	2025-06-23 10:40:43.366098	\N
7072	181	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:43.454079	2025-06-23 10:40:43.454084	\N
7073	179	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:43.542427	2025-06-23 10:40:43.542432	\N
7074	226	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:43.630177	2025-06-23 10:40:43.630181	\N
7075	227	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:43.718662	2025-06-23 10:40:43.718666	\N
7076	193	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:45.894877	2025-06-23 10:40:45.894881	\N
7077	190	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:45.983757	2025-06-23 10:40:45.983762	\N
7078	192	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:46.072269	2025-06-23 10:40:46.072274	\N
7079	191	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:46.160895	2025-06-23 10:40:46.160899	\N
7080	189	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:46.248871	2025-06-23 10:40:46.248876	\N
7081	214	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:51.134369	2025-06-23 10:40:51.134374	\N
7082	194	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:51.222973	2025-06-23 10:40:51.222978	\N
7083	195	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:51.311017	2025-06-23 10:40:51.311022	\N
7084	196	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:51.39896	2025-06-23 10:40:51.398965	\N
7085	197	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:51.487206	2025-06-23 10:40:51.487211	\N
7086	200	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:51.575528	2025-06-23 10:40:51.575533	\N
7087	202	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:51.663453	2025-06-23 10:40:51.663458	\N
7088	203	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:51.751973	2025-06-23 10:40:51.751977	\N
7089	205	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:51.839997	2025-06-23 10:40:51.840001	\N
7090	206	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:51.928591	2025-06-23 10:40:51.928595	\N
7091	207	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:52.016972	2025-06-23 10:40:52.016977	\N
7092	208	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:52.104696	2025-06-23 10:40:52.104701	\N
7093	209	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:52.192938	2025-06-23 10:40:52.192943	\N
7094	198	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:52.281002	2025-06-23 10:40:52.281006	\N
7095	201	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:52.369304	2025-06-23 10:40:52.369308	\N
7096	204	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:52.457096	2025-06-23 10:40:52.457101	\N
7097	225	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:52.545852	2025-06-23 10:40:52.545856	\N
7098	230	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:52.634062	2025-06-23 10:40:52.634067	\N
7099	231	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:52.722029	2025-06-23 10:40:52.722033	\N
7100	216	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:55.534013	2025-06-23 10:40:55.534017	\N
7101	217	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:55.621779	2025-06-23 10:40:55.621783	\N
7102	218	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:55.709632	2025-06-23 10:40:55.709637	\N
7103	219	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:55.79935	2025-06-23 10:40:55.799356	\N
7104	220	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:55.888131	2025-06-23 10:40:55.888135	\N
7105	221	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:55.976127	2025-06-23 10:40:55.976131	\N
7106	222	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:56.064073	2025-06-23 10:40:56.064077	\N
7107	223	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:57.257541	2025-06-23 10:40:57.257545	\N
676	182	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:22.811055	2025-04-21 23:28:22.811064	1
677	175	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:22.902151	2025-04-21 23:28:22.902158	1
678	173	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:22.989835	2025-04-21 23:28:22.98984	1
679	172	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:23.079076	2025-04-21 23:28:23.079082	1
681	171	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:23.270748	2025-04-21 23:28:23.270755	1
682	174	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:23.361693	2025-04-21 23:28:23.3617	1
683	177	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:23.452053	2025-04-21 23:28:23.45206	1
684	169	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:23.547404	2025-04-21 23:28:23.547411	1
687	180	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:10.54971	2025-04-21 23:30:10.549717	1
688	181	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:10.639908	2025-04-21 23:30:10.639913	1
689	179	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:10.727152	2025-04-21 23:30:10.727157	1
690	178	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:10.813925	2025-04-21 23:30:10.81393	1
7017	169	2025-06-23	\N	\N	present	بسبب قرار  ارامكس  ايقاف 8 مندوبين 	2025-06-23 10:35:51.743665	2025-06-24 10:37:22.25227	\N
7108	224	2025-06-22	\N	\N	present	\N	2025-06-23 10:40:57.346155	2025-06-23 10:40:57.34616	\N
7016	177	2025-06-23	\N	\N	present	بسبب قرار  ارامكس  ايقاف 8 مندوبين 	2025-06-23 10:35:51.65596	2025-06-24 10:37:22.161111	\N
7019	181	2025-06-23	\N	\N	present	بسبب قرار  ارامكس  ايقاف 8 مندوبين 	2025-06-23 10:35:51.919426	2025-06-24 10:37:22.479241	\N
7020	179	2025-06-23	\N	\N	present	تم الايقاف بسبب الا طلب ارامكس الاخيره	2025-06-23 10:35:52.007047	2025-06-24 10:37:22.570336	\N
7021	226	2025-06-23	\N	\N	present	بسبب قرار  ارامكس  ايقاف 8 مندوبين 	2025-06-23 10:35:52.09429	2025-06-24 10:37:22.66123	\N
783	180	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:42.358332	2025-04-21 23:36:42.358337	1
784	181	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:42.445359	2025-04-21 23:36:42.445391	1
785	179	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:42.53168	2025-04-21 23:36:42.531685	1
7189	195	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:22.775071	2025-06-25 11:52:22.775075	\N
7190	196	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:22.86982	2025-06-25 11:52:22.869825	\N
7109	184	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:18.785403	2025-06-24 10:37:18.785407	\N
7110	185	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:18.893927	2025-06-24 10:37:18.893931	\N
7111	186	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:18.985975	2025-06-24 10:37:18.98598	\N
7112	187	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:19.077649	2025-06-24 10:37:19.077653	\N
7113	188	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:19.16911	2025-06-24 10:37:19.169112	\N
7009	178	2025-06-23	\N	\N	present	بسبب قرار  ارامكس  ايقاف 8 مندوبين 	2025-06-23 10:35:51.040509	2025-06-24 10:37:21.745836	\N
7011	182	2025-06-23	\N	\N	present	بسبب قرار  ارامكس  ايقاف 8 مندوبين 	2025-06-23 10:35:51.215456	2025-06-24 10:37:21.883669	\N
7018	183	2025-06-23	\N	\N	present	بسبب قرار  ارامكس  ايقاف 8 مندوبين 	2025-06-23 10:35:51.832017	2025-06-24 10:37:22.387926	\N
7114	175	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:22.79948	2025-06-24 10:37:22.799484	\N
7115	178	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:22.893225	2025-06-24 10:37:22.893229	\N
7116	180	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:22.984333	2025-06-24 10:37:22.984338	\N
7117	182	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.075615	2025-06-24 10:37:23.07562	\N
7118	173	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.16704	2025-06-24 10:37:23.167044	\N
7119	172	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.258099	2025-06-24 10:37:23.258105	\N
7120	171	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.352714	2025-06-24 10:37:23.352718	\N
7121	174	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.444709	2025-06-24 10:37:23.444735	\N
7122	177	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.535934	2025-06-24 10:37:23.535938	\N
7123	169	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.628919	2025-06-24 10:37:23.628923	\N
7124	183	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.719857	2025-06-24 10:37:23.719861	\N
7125	181	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.812414	2025-06-24 10:37:23.812418	\N
7126	179	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.90356	2025-06-24 10:37:23.903565	\N
7127	226	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:23.995379	2025-06-24 10:37:23.995384	\N
7128	227	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:24.086924	2025-06-24 10:37:24.086927	\N
7129	193	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:25.424625	2025-06-24 10:37:25.42463	\N
7130	190	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:25.51604	2025-06-24 10:37:25.516044	\N
7131	192	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:25.607418	2025-06-24 10:37:25.607423	\N
7132	191	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:25.698644	2025-06-24 10:37:25.698648	\N
7133	189	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:25.789956	2025-06-24 10:37:25.789959	\N
7134	214	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:29.7234	2025-06-24 10:37:29.723405	\N
7135	194	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:29.814936	2025-06-24 10:37:29.81494	\N
7136	195	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:29.906317	2025-06-24 10:37:29.906334	\N
7137	196	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:29.99767	2025-06-24 10:37:29.997675	\N
7138	197	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:30.088764	2025-06-24 10:37:30.088768	\N
7139	200	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:30.180252	2025-06-24 10:37:30.180257	\N
7140	202	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:30.273812	2025-06-24 10:37:30.273817	\N
7141	203	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:30.365274	2025-06-24 10:37:30.365278	\N
7142	205	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:30.457306	2025-06-24 10:37:30.457311	\N
7143	206	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:30.548884	2025-06-24 10:37:30.548889	\N
7144	207	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:30.640667	2025-06-24 10:37:30.640671	\N
7145	208	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:30.73206	2025-06-24 10:37:30.732064	\N
7146	209	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:30.82579	2025-06-24 10:37:30.825795	\N
7147	198	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:30.917432	2025-06-24 10:37:30.917436	\N
7148	201	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:31.012842	2025-06-24 10:37:31.012846	\N
7149	204	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:31.135742	2025-06-24 10:37:31.135746	\N
7150	225	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:31.227327	2025-06-24 10:37:31.227331	\N
7151	230	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:31.322405	2025-06-24 10:37:31.32241	\N
7152	231	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:31.413537	2025-06-24 10:37:31.41354	\N
7153	216	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:33.184468	2025-06-24 10:37:33.184472	\N
7154	217	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:33.276903	2025-06-24 10:37:33.276907	\N
7155	218	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:33.368324	2025-06-24 10:37:33.368329	\N
7156	219	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:33.460531	2025-06-24 10:37:33.460535	\N
7157	220	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:33.553669	2025-06-24 10:37:33.553673	\N
7158	221	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:33.645782	2025-06-24 10:37:33.645787	\N
7159	222	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:33.737849	2025-06-24 10:37:33.737852	\N
7160	223	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:34.519116	2025-06-24 10:37:34.51912	\N
7161	224	2025-06-24	\N	\N	present	\N	2025-06-24 10:37:34.611762	2025-06-24 10:37:34.611764	\N
7162	184	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:19.207833	2025-06-25 11:52:19.207837	\N
7163	185	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:19.312926	2025-06-25 11:52:19.312931	\N
7164	186	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:19.405788	2025-06-25 11:52:19.405792	\N
7165	187	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:19.498367	2025-06-25 11:52:19.498371	\N
7166	188	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:19.591114	2025-06-25 11:52:19.591117	\N
7167	175	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.041204	2025-06-25 11:52:20.041208	\N
7168	178	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.134872	2025-06-25 11:52:20.134876	\N
7169	180	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.228521	2025-06-25 11:52:20.228525	\N
7170	182	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.320627	2025-06-25 11:52:20.320632	\N
7171	173	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.41279	2025-06-25 11:52:20.412795	\N
7172	172	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.50711	2025-06-25 11:52:20.507114	\N
7173	171	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.599206	2025-06-25 11:52:20.599211	\N
7174	174	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.691256	2025-06-25 11:52:20.691261	\N
7175	177	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.783311	2025-06-25 11:52:20.783316	\N
7176	169	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.875427	2025-06-25 11:52:20.875432	\N
7177	183	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:20.96791	2025-06-25 11:52:20.967915	\N
7178	181	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:21.0604	2025-06-25 11:52:21.060405	\N
7179	179	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:21.152626	2025-06-25 11:52:21.152631	\N
7180	226	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:21.254413	2025-06-25 11:52:21.254418	\N
7181	227	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:21.354259	2025-06-25 11:52:21.354261	\N
7182	193	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:21.797875	2025-06-25 11:52:21.797879	\N
7183	190	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:21.890409	2025-06-25 11:52:21.890413	\N
7184	192	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:21.984225	2025-06-25 11:52:21.98423	\N
7185	191	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:22.083516	2025-06-25 11:52:22.08352	\N
7186	189	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:22.179442	2025-06-25 11:52:22.179444	\N
7187	214	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:22.590898	2025-06-25 11:52:22.590902	\N
7188	194	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:22.683272	2025-06-25 11:52:22.683277	\N
7191	197	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:22.962314	2025-06-25 11:52:22.962318	\N
7192	200	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.055895	2025-06-25 11:52:23.0559	\N
7193	202	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.151275	2025-06-25 11:52:23.151279	\N
7194	203	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.24564	2025-06-25 11:52:23.245645	\N
7195	205	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.338032	2025-06-25 11:52:23.338037	\N
7196	206	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.431311	2025-06-25 11:52:23.431316	\N
7197	207	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.525839	2025-06-25 11:52:23.525844	\N
7198	208	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.621882	2025-06-25 11:52:23.621887	\N
7199	209	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.71443	2025-06-25 11:52:23.714434	\N
7200	198	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.807734	2025-06-25 11:52:23.807738	\N
7201	201	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.899693	2025-06-25 11:52:23.899697	\N
7202	204	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:23.992765	2025-06-25 11:52:23.99277	\N
7203	225	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:24.084786	2025-06-25 11:52:24.084791	\N
7204	230	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:24.177405	2025-06-25 11:52:24.17741	\N
7205	231	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:24.27083	2025-06-25 11:52:24.270832	\N
7206	216	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:24.684637	2025-06-25 11:52:24.684642	\N
889	188	2025-04-18	\N	\N	present	\N	2025-04-22 10:12:22.098966	2025-04-22 10:12:22.098973	1
890	184	2025-04-19	\N	\N	present	\N	2025-04-22 10:12:55.294457	2025-04-22 10:12:55.294462	1
891	185	2025-04-19	\N	\N	present	\N	2025-04-22 10:12:55.429212	2025-04-22 10:12:55.429217	1
7207	217	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:24.776292	2025-06-25 11:52:24.776297	\N
7208	218	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:24.86943	2025-06-25 11:52:24.869434	\N
7209	219	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:24.961486	2025-06-25 11:52:24.961491	\N
7210	220	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:25.053802	2025-06-25 11:52:25.053806	\N
7211	221	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:25.145884	2025-06-25 11:52:25.145889	\N
7212	222	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:25.237481	2025-06-25 11:52:25.237483	\N
7213	223	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:25.655875	2025-06-25 11:52:25.655879	\N
7214	224	2025-06-25	\N	\N	present	\N	2025-06-25 11:52:25.748168	2025-06-25 11:52:25.74817	\N
7215	184	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:50.774572	2025-06-26 11:22:50.774577	\N
7216	185	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:50.88769	2025-06-26 11:22:50.887694	\N
7217	186	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:50.981177	2025-06-26 11:22:50.981182	\N
7218	187	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:51.073647	2025-06-26 11:22:51.073652	\N
7219	188	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:51.162822	2025-06-26 11:22:51.162824	\N
7220	175	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:51.581618	2025-06-26 11:22:51.581623	\N
7221	178	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:51.681213	2025-06-26 11:22:51.681217	\N
7222	180	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:51.777411	2025-06-26 11:22:51.777416	\N
7223	182	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:51.86903	2025-06-26 11:22:51.869034	\N
7224	173	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:51.969079	2025-06-26 11:22:51.969084	\N
7225	172	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:52.058229	2025-06-26 11:22:52.058234	\N
7226	171	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:52.147482	2025-06-26 11:22:52.147486	\N
7227	174	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:52.242135	2025-06-26 11:22:52.24214	\N
7228	177	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:52.331597	2025-06-26 11:22:52.331602	\N
7229	169	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:52.421233	2025-06-26 11:22:52.421238	\N
7230	183	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:52.510378	2025-06-26 11:22:52.510382	\N
7231	181	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:52.599938	2025-06-26 11:22:52.599943	\N
7232	179	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:52.689448	2025-06-26 11:22:52.689454	\N
7233	226	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:52.78774	2025-06-26 11:22:52.787744	\N
7234	227	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:52.884605	2025-06-26 11:22:52.884607	\N
7235	193	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:53.296351	2025-06-26 11:22:53.296355	\N
7236	190	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:53.386545	2025-06-26 11:22:53.38655	\N
7237	192	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:53.475989	2025-06-26 11:22:53.475995	\N
7238	191	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:53.572527	2025-06-26 11:22:53.572532	\N
7239	189	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:53.665549	2025-06-26 11:22:53.665552	\N
7240	214	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.071829	2025-06-26 11:22:54.071834	\N
7241	194	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.16255	2025-06-26 11:22:54.162554	\N
7242	195	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.25194	2025-06-26 11:22:54.251945	\N
7243	196	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.343589	2025-06-26 11:22:54.343595	\N
7244	197	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.434069	2025-06-26 11:22:54.434074	\N
7245	200	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.531926	2025-06-26 11:22:54.531931	\N
7246	202	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.62261	2025-06-26 11:22:54.622614	\N
7247	203	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.714912	2025-06-26 11:22:54.714917	\N
7248	205	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.806602	2025-06-26 11:22:54.806607	\N
7249	206	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.902944	2025-06-26 11:22:54.902949	\N
7250	207	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:54.992855	2025-06-26 11:22:54.992859	\N
7251	208	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:55.083007	2025-06-26 11:22:55.083012	\N
7252	209	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:55.173583	2025-06-26 11:22:55.173588	\N
7253	198	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:55.263743	2025-06-26 11:22:55.263747	\N
7254	201	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:55.361109	2025-06-26 11:22:55.361114	\N
7255	204	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:55.451088	2025-06-26 11:22:55.451093	\N
7256	225	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:55.546085	2025-06-26 11:22:55.546089	\N
7257	230	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:55.6428	2025-06-26 11:22:55.642805	\N
7258	231	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:55.732946	2025-06-26 11:22:55.732948	\N
7259	216	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:56.141829	2025-06-26 11:22:56.141834	\N
7260	217	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:56.241368	2025-06-26 11:22:56.241373	\N
7261	218	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:56.337616	2025-06-26 11:22:56.337621	\N
7262	219	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:56.4288	2025-06-26 11:22:56.428804	\N
7263	220	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:56.518608	2025-06-26 11:22:56.518613	\N
7264	221	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:56.611004	2025-06-26 11:22:56.611009	\N
7265	222	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:56.703061	2025-06-26 11:22:56.703065	\N
7266	223	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:57.108381	2025-06-26 11:22:57.108386	\N
7267	224	2025-06-26	\N	\N	present	\N	2025-06-26 11:22:57.202239	2025-06-26 11:22:57.202242	\N
7268	184	2025-06-27	\N	\N	present	\N	2025-06-28 10:43:59.170602	2025-06-28 10:43:59.170606	\N
7269	185	2025-06-27	\N	\N	present	\N	2025-06-28 10:43:59.276862	2025-06-28 10:43:59.276867	\N
7270	186	2025-06-27	\N	\N	present	\N	2025-06-28 10:43:59.367291	2025-06-28 10:43:59.367295	\N
7271	187	2025-06-27	\N	\N	present	\N	2025-06-28 10:43:59.457729	2025-06-28 10:43:59.457734	\N
7272	188	2025-06-27	\N	\N	present	\N	2025-06-28 10:43:59.548622	2025-06-28 10:43:59.548627	\N
7273	184	2025-06-28	\N	\N	present	\N	2025-06-28 10:43:59.639291	2025-06-28 10:43:59.639296	\N
7274	185	2025-06-28	\N	\N	present	\N	2025-06-28 10:43:59.729875	2025-06-28 10:43:59.72988	\N
7275	186	2025-06-28	\N	\N	present	\N	2025-06-28 10:43:59.820631	2025-06-28 10:43:59.820635	\N
7276	187	2025-06-28	\N	\N	present	\N	2025-06-28 10:43:59.912999	2025-06-28 10:43:59.913008	\N
7277	188	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:00.003909	2025-06-28 10:44:00.003912	\N
7278	175	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:03.920658	2025-06-28 10:44:03.920663	\N
7279	178	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.013682	2025-06-28 10:44:04.013687	\N
7280	180	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.104938	2025-06-28 10:44:04.104942	\N
7281	182	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.195492	2025-06-28 10:44:04.195496	\N
7282	173	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.286799	2025-06-28 10:44:04.286803	\N
7283	172	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.378006	2025-06-28 10:44:04.37801	\N
7284	171	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.469285	2025-06-28 10:44:04.469289	\N
7285	174	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.560533	2025-06-28 10:44:04.56054	\N
7286	177	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.652822	2025-06-28 10:44:04.652826	\N
7287	169	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.745071	2025-06-28 10:44:04.745075	\N
7288	183	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.835881	2025-06-28 10:44:04.835886	\N
7289	181	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:04.927648	2025-06-28 10:44:04.927654	\N
7290	179	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:05.019985	2025-06-28 10:44:05.019994	\N
7291	226	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:05.111577	2025-06-28 10:44:05.111581	\N
7292	227	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:05.202571	2025-06-28 10:44:05.20258	\N
7293	175	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:05.293438	2025-06-28 10:44:05.293443	\N
7294	178	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:05.384803	2025-06-28 10:44:05.384815	\N
7295	180	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:05.479544	2025-06-28 10:44:05.479549	\N
7296	182	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:05.571025	2025-06-28 10:44:05.571033	\N
7297	173	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:05.662996	2025-06-28 10:44:05.663003	\N
7298	172	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:05.754163	2025-06-28 10:44:05.754169	\N
7299	171	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:05.844845	2025-06-28 10:44:05.84485	\N
7300	174	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:05.935647	2025-06-28 10:44:05.935651	\N
7301	177	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:06.026271	2025-06-28 10:44:06.026275	\N
7302	169	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:06.116631	2025-06-28 10:44:06.116635	\N
7303	183	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:06.20739	2025-06-28 10:44:06.207394	\N
7304	181	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:06.29781	2025-06-28 10:44:06.297815	\N
995	192	2025-04-13	\N	\N	present	\N	2025-04-23 10:25:29.190607	2025-04-23 10:25:29.190611	1
996	193	2025-04-13	\N	\N	present	\N	2025-04-23 10:25:29.284379	2025-04-23 10:25:29.284384	1
997	189	2025-04-14	\N	\N	present	\N	2025-04-23 10:25:43.264437	2025-04-23 10:25:43.264442	1
998	190	2025-04-14	\N	\N	present	\N	2025-04-23 10:25:43.353706	2025-04-23 10:25:43.353711	1
999	191	2025-04-14	\N	\N	present	\N	2025-04-23 10:25:43.442904	2025-04-23 10:25:43.442909	1
1000	192	2025-04-14	\N	\N	present	\N	2025-04-23 10:25:43.53311	2025-04-23 10:25:43.533116	1
1001	193	2025-04-14	\N	\N	present	\N	2025-04-23 10:25:43.621292	2025-04-23 10:25:43.621297	1
1002	189	2025-04-23	\N	\N	present	\N	2025-04-23 10:26:03.625518	2025-04-23 10:26:03.625523	1
7305	179	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:06.388615	2025-06-28 10:44:06.388619	\N
7306	226	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:06.480069	2025-06-28 10:44:06.480074	\N
7307	227	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:06.571536	2025-06-28 10:44:06.571539	\N
7308	193	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:08.17072	2025-06-28 10:44:08.170724	\N
7309	190	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:08.261335	2025-06-28 10:44:08.26134	\N
7310	192	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:08.352063	2025-06-28 10:44:08.352068	\N
7311	191	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:08.443434	2025-06-28 10:44:08.443438	\N
7312	189	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:08.534051	2025-06-28 10:44:08.534055	\N
7313	193	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:08.625947	2025-06-28 10:44:08.625957	\N
7314	190	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:08.717941	2025-06-28 10:44:08.717949	\N
7315	192	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:08.808769	2025-06-28 10:44:08.808773	\N
7316	191	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:08.89997	2025-06-28 10:44:08.899975	\N
7317	189	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:09.001463	2025-06-28 10:44:09.001466	\N
7318	214	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:13.832965	2025-06-28 10:44:13.832974	\N
7319	194	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:13.924542	2025-06-28 10:44:13.924551	\N
7320	195	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.015168	2025-06-28 10:44:14.015173	\N
7321	196	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.105884	2025-06-28 10:44:14.105889	\N
7322	197	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.196985	2025-06-28 10:44:14.19699	\N
7323	200	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.287546	2025-06-28 10:44:14.287551	\N
7324	202	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.37835	2025-06-28 10:44:14.378481	\N
7325	203	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.469506	2025-06-28 10:44:14.469511	\N
7326	205	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.560139	2025-06-28 10:44:14.560144	\N
7327	206	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.657327	2025-06-28 10:44:14.657332	\N
7328	207	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.748202	2025-06-28 10:44:14.748207	\N
7329	208	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.838607	2025-06-28 10:44:14.838611	\N
7330	209	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:14.928943	2025-06-28 10:44:14.928948	\N
7331	198	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:15.019191	2025-06-28 10:44:15.019195	\N
7332	201	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:15.10944	2025-06-28 10:44:15.109445	\N
7333	204	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:15.199744	2025-06-28 10:44:15.199748	\N
7334	225	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:15.290239	2025-06-28 10:44:15.290244	\N
7335	230	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:15.381114	2025-06-28 10:44:15.381118	\N
7336	231	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:15.471374	2025-06-28 10:44:15.471378	\N
7337	214	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:15.56184	2025-06-28 10:44:15.561845	\N
7338	194	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:15.654644	2025-06-28 10:44:15.654648	\N
7339	195	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:15.745803	2025-06-28 10:44:15.74581	\N
7340	196	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:15.837285	2025-06-28 10:44:15.83729	\N
7341	197	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:15.92829	2025-06-28 10:44:15.928295	\N
7342	200	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.019517	2025-06-28 10:44:16.019521	\N
7343	202	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.114044	2025-06-28 10:44:16.114048	\N
7344	203	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.207599	2025-06-28 10:44:16.207608	\N
7345	205	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.29965	2025-06-28 10:44:16.299655	\N
7346	206	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.390528	2025-06-28 10:44:16.390533	\N
7347	207	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.487661	2025-06-28 10:44:16.487666	\N
7348	208	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.579587	2025-06-28 10:44:16.579592	\N
7349	209	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.673242	2025-06-28 10:44:16.673246	\N
7350	198	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.764071	2025-06-28 10:44:16.764077	\N
7351	201	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.857239	2025-06-28 10:44:16.857247	\N
7352	204	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:16.95023	2025-06-28 10:44:16.950239	\N
7353	225	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:17.041383	2025-06-28 10:44:17.041387	\N
7354	230	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:17.134347	2025-06-28 10:44:17.134355	\N
7355	231	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:17.225729	2025-06-28 10:44:17.225731	\N
7356	216	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:19.239112	2025-06-28 10:44:19.239117	\N
7357	217	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:19.331079	2025-06-28 10:44:19.331084	\N
7358	218	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:19.422607	2025-06-28 10:44:19.422612	\N
7359	219	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:19.513354	2025-06-28 10:44:19.513359	\N
7360	220	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:19.604328	2025-06-28 10:44:19.604333	\N
7361	221	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:19.69506	2025-06-28 10:44:19.695065	\N
7362	222	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:19.786622	2025-06-28 10:44:19.786628	\N
7363	216	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:19.878277	2025-06-28 10:44:19.878281	\N
7364	217	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:19.969324	2025-06-28 10:44:19.969329	\N
7365	218	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:20.059707	2025-06-28 10:44:20.059711	\N
7366	219	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:20.151035	2025-06-28 10:44:20.151039	\N
7367	220	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:20.242615	2025-06-28 10:44:20.242622	\N
7368	221	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:20.335149	2025-06-28 10:44:20.335159	\N
7369	222	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:20.42684	2025-06-28 10:44:20.426843	\N
7370	223	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:21.298443	2025-06-28 10:44:21.298447	\N
7371	224	2025-06-27	\N	\N	present	\N	2025-06-28 10:44:21.389626	2025-06-28 10:44:21.389631	\N
7372	223	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:21.480058	2025-06-28 10:44:21.480062	\N
7373	224	2025-06-28	\N	\N	present	\N	2025-06-28 10:44:21.570785	2025-06-28 10:44:21.570788	\N
7374	184	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:33.207906	2025-06-29 18:37:33.207913	\N
7375	185	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:33.343218	2025-06-29 18:37:33.343223	\N
7376	186	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:33.434229	2025-06-29 18:37:33.434234	\N
7377	187	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:33.524926	2025-06-29 18:37:33.52493	\N
7378	188	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:33.621669	2025-06-29 18:37:33.621672	\N
7379	175	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:36.820326	2025-06-29 18:37:36.820331	\N
7380	178	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:36.911345	2025-06-29 18:37:36.911351	\N
7381	180	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.002292	2025-06-29 18:37:37.002297	\N
7382	182	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.09293	2025-06-29 18:37:37.092935	\N
7383	173	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.183337	2025-06-29 18:37:37.183342	\N
7384	172	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.27453	2025-06-29 18:37:37.274535	\N
7385	171	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.365278	2025-06-29 18:37:37.365282	\N
7386	174	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.456234	2025-06-29 18:37:37.456239	\N
7387	177	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.547191	2025-06-29 18:37:37.547196	\N
7388	169	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.637836	2025-06-29 18:37:37.63784	\N
7389	183	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.728182	2025-06-29 18:37:37.728188	\N
7390	181	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.819079	2025-06-29 18:37:37.819084	\N
7391	179	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:37.909696	2025-06-29 18:37:37.9097	\N
7392	226	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:38.000147	2025-06-29 18:37:38.000152	\N
7393	227	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:38.090606	2025-06-29 18:37:38.090609	\N
7394	193	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:39.494617	2025-06-29 18:37:39.494622	\N
7395	190	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:39.585344	2025-06-29 18:37:39.585349	\N
7396	192	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:39.676229	2025-06-29 18:37:39.676235	\N
7397	191	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:39.766791	2025-06-29 18:37:39.766796	\N
2575	202	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:01.972293	2025-04-23 13:36:01.972296	1
2576	203	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:02.059009	2025-04-23 13:36:02.059013	1
2577	204	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:02.145603	2025-04-23 13:36:02.145608	1
2578	205	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:02.233528	2025-04-23 13:36:02.233531	1
2579	206	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:02.320377	2025-04-23 13:36:02.320382	1
2580	207	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:02.407791	2025-04-23 13:36:02.407795	1
2581	208	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:02.495812	2025-04-23 13:36:02.495816	1
2582	209	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:02.582562	2025-04-23 13:36:02.582565	1
2583	210	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:02.670769	2025-04-23 13:36:02.670773	1
2584	211	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:02.757563	2025-04-23 13:36:02.757567	1
2585	212	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:02.847876	2025-04-23 13:36:02.847879	1
2587	214	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:03.023577	2025-04-23 13:36:03.02358	1
7398	189	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:39.857506	2025-06-29 18:37:39.857509	\N
7399	214	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:43.822733	2025-06-29 18:37:43.822738	\N
7400	194	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:43.914328	2025-06-29 18:37:43.914334	\N
7401	195	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.005496	2025-06-29 18:37:44.005502	\N
7402	196	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.096775	2025-06-29 18:37:44.096781	\N
7403	197	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.187412	2025-06-29 18:37:44.187417	\N
7404	200	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.278665	2025-06-29 18:37:44.27867	\N
7405	202	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.370047	2025-06-29 18:37:44.370052	\N
7406	203	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.460754	2025-06-29 18:37:44.460759	\N
7407	205	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.551947	2025-06-29 18:37:44.551953	\N
7408	206	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.642964	2025-06-29 18:37:44.64297	\N
7409	207	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.733976	2025-06-29 18:37:44.733984	\N
7410	208	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.825576	2025-06-29 18:37:44.825581	\N
7411	209	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:44.916311	2025-06-29 18:37:44.916316	\N
7412	198	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:45.007573	2025-06-29 18:37:45.007578	\N
7413	201	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:45.099434	2025-06-29 18:37:45.09944	\N
7414	204	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:45.192296	2025-06-29 18:37:45.192305	\N
7415	225	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:45.284393	2025-06-29 18:37:45.284398	\N
7416	230	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:45.375048	2025-06-29 18:37:45.375053	\N
7417	231	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:45.465652	2025-06-29 18:37:45.465655	\N
7418	216	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:47.162228	2025-06-29 18:37:47.162232	\N
7419	217	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:47.252666	2025-06-29 18:37:47.25267	\N
7420	218	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:47.343208	2025-06-29 18:37:47.343213	\N
7421	219	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:47.435741	2025-06-29 18:37:47.435746	\N
7422	220	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:47.525914	2025-06-29 18:37:47.525918	\N
7423	221	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:47.616694	2025-06-29 18:37:47.616698	\N
7424	222	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:47.707016	2025-06-29 18:37:47.707018	\N
7425	223	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:48.477856	2025-06-29 18:37:48.477861	\N
7426	224	2025-06-29	\N	\N	present	\N	2025-06-29 18:37:48.570943	2025-06-29 18:37:48.570946	\N
7427	184	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:50.157444	2025-06-29 18:37:50.157449	\N
7428	185	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:50.248181	2025-06-29 18:37:50.248186	\N
7429	186	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:50.33876	2025-06-29 18:37:50.338764	\N
7430	187	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:50.42946	2025-06-29 18:37:50.429465	\N
7431	188	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:50.519632	2025-06-29 18:37:50.519634	\N
7432	175	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:54.402021	2025-06-29 18:37:54.402027	\N
7433	178	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:54.49312	2025-06-29 18:37:54.493125	\N
7434	180	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:54.583899	2025-06-29 18:37:54.583904	\N
7435	182	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:54.675891	2025-06-29 18:37:54.675897	\N
7436	173	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:54.768253	2025-06-29 18:37:54.768259	\N
7437	172	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:54.861241	2025-06-29 18:37:54.86125	\N
7438	171	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:54.953362	2025-06-29 18:37:54.953368	\N
7439	174	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:55.04469	2025-06-29 18:37:55.044695	\N
7440	177	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:55.136156	2025-06-29 18:37:55.136162	\N
7441	169	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:55.227232	2025-06-29 18:37:55.227236	\N
7442	183	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:55.319079	2025-06-29 18:37:55.319085	\N
7443	181	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:55.409979	2025-06-29 18:37:55.409984	\N
7444	179	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:55.501414	2025-06-29 18:37:55.501418	\N
7445	226	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:55.59252	2025-06-29 18:37:55.592564	\N
7446	227	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:55.683396	2025-06-29 18:37:55.683399	\N
2683	200	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:45.225732	2025-04-23 13:36:45.225736	1
2684	201	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:45.312912	2025-04-23 13:36:45.312915	1
2685	202	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:45.400003	2025-04-23 13:36:45.400007	1
2686	203	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:45.487122	2025-04-23 13:36:45.487126	1
2687	204	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:45.57384	2025-04-23 13:36:45.573844	1
2688	205	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:45.661345	2025-04-23 13:36:45.66135	1
2689	206	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:45.748327	2025-04-23 13:36:45.74833	1
2690	207	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:45.834872	2025-04-23 13:36:45.834876	1
2691	208	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:45.921843	2025-04-23 13:36:45.921846	1
2692	209	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:46.00842	2025-04-23 13:36:46.008424	1
2693	210	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:46.096196	2025-04-23 13:36:46.0962	1
2694	211	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:46.183093	2025-04-23 13:36:46.183097	1
2695	212	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:46.270121	2025-04-23 13:36:46.270125	1
7447	193	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:57.486501	2025-06-29 18:37:57.486506	\N
7448	190	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:57.579443	2025-06-29 18:37:57.579448	\N
7449	192	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:57.67257	2025-06-29 18:37:57.672575	\N
7450	191	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:57.766561	2025-06-29 18:37:57.766565	\N
7451	189	2025-06-30	\N	\N	present	\N	2025-06-29 18:37:57.858809	2025-06-29 18:37:57.858811	\N
7452	214	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:02.707943	2025-06-29 18:38:02.707949	\N
7453	194	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:02.800996	2025-06-29 18:38:02.801001	\N
7454	195	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:02.893154	2025-06-29 18:38:02.89316	\N
7455	196	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:02.985186	2025-06-29 18:38:02.985191	\N
7456	197	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:03.077133	2025-06-29 18:38:03.077138	\N
7457	200	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:03.170799	2025-06-29 18:38:03.170804	\N
7458	202	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:03.263454	2025-06-29 18:38:03.263459	\N
7459	203	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:03.356447	2025-06-29 18:38:03.356453	\N
7460	205	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:03.451136	2025-06-29 18:38:03.451141	\N
7461	206	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:03.546693	2025-06-29 18:38:03.546698	\N
7462	207	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:03.641236	2025-06-29 18:38:03.64124	\N
7463	208	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:03.734894	2025-06-29 18:38:03.734899	\N
7464	209	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:03.828321	2025-06-29 18:38:03.828327	\N
7465	198	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:03.921747	2025-06-29 18:38:03.921753	\N
7466	201	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:04.013577	2025-06-29 18:38:04.013582	\N
7467	204	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:04.107022	2025-06-29 18:38:04.107027	\N
7468	225	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:04.199338	2025-06-29 18:38:04.199343	\N
7469	230	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:04.304074	2025-06-29 18:38:04.304079	\N
7470	231	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:04.396405	2025-06-29 18:38:04.396408	\N
7471	216	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:06.446136	2025-06-29 18:38:06.446141	\N
7472	217	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:06.538701	2025-06-29 18:38:06.538706	\N
7473	218	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:06.630736	2025-06-29 18:38:06.630741	\N
7474	219	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:06.722623	2025-06-29 18:38:06.72263	\N
7475	220	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:06.81638	2025-06-29 18:38:06.816384	\N
7476	221	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:06.908288	2025-06-29 18:38:06.908295	\N
7477	222	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:07.000206	2025-06-29 18:38:07.000208	\N
7478	223	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:07.875264	2025-06-29 18:38:07.87527	\N
7479	224	2025-06-30	\N	\N	present	\N	2025-06-29 18:38:07.966742	2025-06-29 18:38:07.966744	\N
2413	194	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:47.760659	2025-04-23 13:35:47.760663	1
2414	195	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:47.849326	2025-04-23 13:35:47.84933	1
2415	196	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:47.936051	2025-04-23 13:35:47.936055	1
2416	197	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.022799	2025-04-23 13:35:48.022802	1
2417	198	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.110121	2025-04-23 13:35:48.110125	1
2419	200	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.284686	2025-04-23 13:35:48.28469	1
2420	201	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.371584	2025-04-23 13:35:48.371587	1
2421	202	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.458963	2025-04-23 13:35:48.458967	1
2422	203	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.545635	2025-04-23 13:35:48.54564	1
2423	204	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.632956	2025-04-23 13:35:48.63296	1
2424	205	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.720108	2025-04-23 13:35:48.720111	1
7480	184	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:40.251694	2025-07-03 12:25:40.251699	\N
7481	185	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:40.367498	2025-07-03 12:25:40.367504	\N
7482	186	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:40.466073	2025-07-03 12:25:40.466079	\N
7483	187	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:40.559096	2025-07-03 12:25:40.559102	\N
7484	188	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:40.652546	2025-07-03 12:25:40.652551	\N
7485	184	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:40.746102	2025-07-03 12:25:40.746107	\N
7486	185	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:40.838965	2025-07-03 12:25:40.83897	\N
7487	186	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:40.932288	2025-07-03 12:25:40.932292	\N
7488	187	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:41.024892	2025-07-03 12:25:41.024897	\N
7489	188	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:41.117439	2025-07-03 12:25:41.117471	\N
7490	184	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:41.210149	2025-07-03 12:25:41.210154	\N
7491	185	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:41.303929	2025-07-03 12:25:41.303934	\N
7492	186	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:41.397162	2025-07-03 12:25:41.397167	\N
7493	187	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:41.499312	2025-07-03 12:25:41.499317	\N
7494	188	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:41.592622	2025-07-03 12:25:41.592624	\N
7495	175	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:42.78205	2025-07-03 12:25:42.782056	\N
7496	178	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:42.881167	2025-07-03 12:25:42.881172	\N
7497	180	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:42.97403	2025-07-03 12:25:42.974036	\N
7498	182	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.066759	2025-07-03 12:25:43.066765	\N
7499	173	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.159141	2025-07-03 12:25:43.159146	\N
7500	172	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.251677	2025-07-03 12:25:43.251682	\N
7501	171	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.34446	2025-07-03 12:25:43.344465	\N
7502	174	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.437178	2025-07-03 12:25:43.437183	\N
7503	177	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.530376	2025-07-03 12:25:43.530381	\N
7504	169	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.62386	2025-07-03 12:25:43.623865	\N
7505	183	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.716831	2025-07-03 12:25:43.716837	\N
7506	181	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.809742	2025-07-03 12:25:43.809747	\N
7507	179	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.902341	2025-07-03 12:25:43.902346	\N
7508	226	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:43.995097	2025-07-03 12:25:43.995103	\N
7509	227	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:44.087919	2025-07-03 12:25:44.087924	\N
7510	175	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:44.181656	2025-07-03 12:25:44.181662	\N
7511	178	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:44.274299	2025-07-03 12:25:44.274304	\N
7512	180	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:44.367326	2025-07-03 12:25:44.367332	\N
7513	182	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:44.460589	2025-07-03 12:25:44.460594	\N
7514	173	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:44.553707	2025-07-03 12:25:44.553712	\N
7515	172	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:44.662689	2025-07-03 12:25:44.662694	\N
7516	171	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:44.756606	2025-07-03 12:25:44.756611	\N
7517	174	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:44.849713	2025-07-03 12:25:44.849718	\N
7518	177	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:44.950705	2025-07-03 12:25:44.95071	\N
7519	169	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:45.04373	2025-07-03 12:25:45.043735	\N
7520	183	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:45.136718	2025-07-03 12:25:45.136723	\N
7521	181	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:45.229792	2025-07-03 12:25:45.229797	\N
7522	179	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:45.323093	2025-07-03 12:25:45.323098	\N
7523	226	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:45.41625	2025-07-03 12:25:45.416255	\N
7524	227	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:45.509831	2025-07-03 12:25:45.509835	\N
7525	175	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:45.602428	2025-07-03 12:25:45.602433	\N
7526	178	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:45.695575	2025-07-03 12:25:45.695581	\N
7527	180	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:45.788567	2025-07-03 12:25:45.788572	\N
7528	182	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:45.881055	2025-07-03 12:25:45.88106	\N
7529	173	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:45.973636	2025-07-03 12:25:45.973641	\N
7530	172	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:46.066119	2025-07-03 12:25:46.066137	\N
7531	171	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:46.159564	2025-07-03 12:25:46.159569	\N
7532	174	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:46.254327	2025-07-03 12:25:46.254332	\N
7533	177	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:46.347115	2025-07-03 12:25:46.34712	\N
7534	169	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:46.439966	2025-07-03 12:25:46.439972	\N
7535	183	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:46.53311	2025-07-03 12:25:46.533114	\N
7536	181	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:46.625866	2025-07-03 12:25:46.625871	\N
7537	179	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:46.720193	2025-07-03 12:25:46.720199	\N
7538	226	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:46.813414	2025-07-03 12:25:46.813419	\N
7539	227	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:46.906214	2025-07-03 12:25:46.906217	\N
7540	193	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:47.554315	2025-07-03 12:25:47.55432	\N
7541	190	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:47.647144	2025-07-03 12:25:47.647149	\N
7542	192	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:47.740734	2025-07-03 12:25:47.740739	\N
7543	191	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:47.833957	2025-07-03 12:25:47.833963	\N
7544	189	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:47.926616	2025-07-03 12:25:47.926621	\N
7545	193	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:48.021832	2025-07-03 12:25:48.021837	\N
7546	190	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:48.136937	2025-07-03 12:25:48.136942	\N
7547	192	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:48.229494	2025-07-03 12:25:48.2295	\N
7548	191	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:48.323382	2025-07-03 12:25:48.323386	\N
7549	189	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:48.416236	2025-07-03 12:25:48.416241	\N
7550	193	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:48.509233	2025-07-03 12:25:48.509238	\N
7551	190	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:48.602517	2025-07-03 12:25:48.602522	\N
7552	192	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:48.695141	2025-07-03 12:25:48.695145	\N
7553	191	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:48.790106	2025-07-03 12:25:48.790112	\N
7554	189	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:48.883075	2025-07-03 12:25:48.883077	\N
7555	214	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:50.190412	2025-07-03 12:25:50.190418	\N
7556	194	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:50.283457	2025-07-03 12:25:50.283463	\N
7557	195	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:50.376547	2025-07-03 12:25:50.376552	\N
7558	196	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:50.469145	2025-07-03 12:25:50.469151	\N
7559	197	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:50.563919	2025-07-03 12:25:50.563924	\N
7560	200	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:50.657642	2025-07-03 12:25:50.657648	\N
7561	202	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:50.752161	2025-07-03 12:25:50.752166	\N
7562	203	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:50.846347	2025-07-03 12:25:50.846353	\N
7563	205	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:50.939236	2025-07-03 12:25:50.939241	\N
7564	206	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:51.031899	2025-07-03 12:25:51.031904	\N
7565	207	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:51.124902	2025-07-03 12:25:51.124907	\N
7566	208	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:51.217976	2025-07-03 12:25:51.217981	\N
7567	209	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:51.310577	2025-07-03 12:25:51.310581	\N
7568	198	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:51.403586	2025-07-03 12:25:51.403592	\N
7569	201	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:51.498215	2025-07-03 12:25:51.498221	\N
7570	204	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:51.591713	2025-07-03 12:25:51.591717	\N
7571	225	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:51.684559	2025-07-03 12:25:51.684564	\N
7572	230	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:51.777275	2025-07-03 12:25:51.77728	\N
2772	201	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.038008	2025-04-23 13:36:53.038012	1
2773	202	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.124837	2025-04-23 13:36:53.124842	1
2774	203	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.212049	2025-04-23 13:36:53.212053	1
2775	204	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.299022	2025-04-23 13:36:53.299025	1
2776	205	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.386527	2025-04-23 13:36:53.38653	1
2777	206	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.472984	2025-04-23 13:36:53.472988	1
2778	207	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.559748	2025-04-23 13:36:53.559751	1
2779	208	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.646207	2025-04-23 13:36:53.646211	1
2780	209	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.73285	2025-04-23 13:36:53.732854	1
2781	210	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.823266	2025-04-23 13:36:53.823273	1
2782	211	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.909953	2025-04-23 13:36:53.909956	1
2783	212	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:53.996586	2025-04-23 13:36:53.99659	1
7573	231	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:51.873669	2025-07-03 12:25:51.873673	\N
7574	214	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:51.974755	2025-07-03 12:25:51.97476	\N
7575	194	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:52.068602	2025-07-03 12:25:52.068608	\N
7576	195	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:52.16155	2025-07-03 12:25:52.161556	\N
7577	196	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:52.254114	2025-07-03 12:25:52.254158	\N
7578	197	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:52.34706	2025-07-03 12:25:52.347065	\N
7579	200	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:52.441766	2025-07-03 12:25:52.441771	\N
7580	202	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:52.534575	2025-07-03 12:25:52.53458	\N
7581	203	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:52.630727	2025-07-03 12:25:52.630732	\N
7582	205	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:52.723678	2025-07-03 12:25:52.723684	\N
7583	206	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:52.817559	2025-07-03 12:25:52.817564	\N
7584	207	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:52.911459	2025-07-03 12:25:52.911464	\N
7585	208	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:53.0097	2025-07-03 12:25:53.009705	\N
7586	209	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:53.117874	2025-07-03 12:25:53.117879	\N
7587	198	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:53.211697	2025-07-03 12:25:53.211702	\N
7588	201	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:53.30453	2025-07-03 12:25:53.304534	\N
7589	204	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:53.397333	2025-07-03 12:25:53.397338	\N
7590	225	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:53.494085	2025-07-03 12:25:53.49409	\N
7591	230	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:53.586845	2025-07-03 12:25:53.58685	\N
7592	231	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:53.681008	2025-07-03 12:25:53.681013	\N
7593	214	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:53.774045	2025-07-03 12:25:53.77405	\N
7594	194	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:53.866834	2025-07-03 12:25:53.866839	\N
7595	195	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:53.959899	2025-07-03 12:25:53.959905	\N
7596	196	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.052919	2025-07-03 12:25:54.052925	\N
7597	197	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.146102	2025-07-03 12:25:54.146107	\N
7598	200	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.238914	2025-07-03 12:25:54.238918	\N
7599	202	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.331646	2025-07-03 12:25:54.331651	\N
7600	203	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.424547	2025-07-03 12:25:54.424553	\N
7601	205	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.518657	2025-07-03 12:25:54.518662	\N
7602	206	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.612223	2025-07-03 12:25:54.612228	\N
7603	207	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.704615	2025-07-03 12:25:54.70462	\N
7604	208	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.797198	2025-07-03 12:25:54.797203	\N
7605	209	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.893673	2025-07-03 12:25:54.893678	\N
7606	198	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:54.986422	2025-07-03 12:25:54.986427	\N
7607	201	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:55.081605	2025-07-03 12:25:55.081609	\N
7608	204	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:55.175532	2025-07-03 12:25:55.175537	\N
7609	225	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:55.269297	2025-07-03 12:25:55.269303	\N
7610	230	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:55.36596	2025-07-03 12:25:55.365965	\N
7611	231	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:55.46669	2025-07-03 12:25:55.466693	\N
7612	216	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:56.234637	2025-07-03 12:25:56.234642	\N
7613	217	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:56.330391	2025-07-03 12:25:56.330396	\N
7614	218	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:56.426353	2025-07-03 12:25:56.426358	\N
7615	219	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:56.5193	2025-07-03 12:25:56.519304	\N
7616	220	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:56.612292	2025-07-03 12:25:56.612297	\N
7617	221	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:56.70627	2025-07-03 12:25:56.706275	\N
7618	222	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:56.799984	2025-07-03 12:25:56.799989	\N
7619	216	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:56.892681	2025-07-03 12:25:56.892685	\N
7620	217	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:56.985555	2025-07-03 12:25:56.98556	\N
7621	218	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:57.079766	2025-07-03 12:25:57.079771	\N
7622	219	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:57.172777	2025-07-03 12:25:57.172783	\N
7623	220	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:57.266169	2025-07-03 12:25:57.266174	\N
7624	221	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:57.358758	2025-07-03 12:25:57.358763	\N
7625	222	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:57.451678	2025-07-03 12:25:57.451683	\N
7626	216	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:57.54597	2025-07-03 12:25:57.545975	\N
7627	217	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:57.659427	2025-07-03 12:25:57.659431	\N
7628	218	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:57.752158	2025-07-03 12:25:57.752163	\N
7629	219	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:57.845216	2025-07-03 12:25:57.845228	\N
7630	220	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:57.937782	2025-07-03 12:25:57.937787	\N
7631	221	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:58.035398	2025-07-03 12:25:58.035404	\N
7632	222	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:58.129107	2025-07-03 12:25:58.129109	\N
7633	223	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:58.637685	2025-07-03 12:25:58.63769	\N
7634	224	2025-07-01	\N	\N	present	\N	2025-07-03 12:25:58.730886	2025-07-03 12:25:58.730892	\N
7635	223	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:58.826637	2025-07-03 12:25:58.826642	\N
7636	224	2025-07-02	\N	\N	present	\N	2025-07-03 12:25:58.919785	2025-07-03 12:25:58.91979	\N
7637	223	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:59.012552	2025-07-03 12:25:59.012557	\N
7638	224	2025-07-03	\N	\N	present	\N	2025-07-03 12:25:59.105112	2025-07-03 12:25:59.105115	\N
7639	186	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:13.077417	2025-07-06 13:12:13.077493	\N
7640	184	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:13.183821	2025-07-06 13:12:13.183826	\N
7641	185	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:13.275626	2025-07-06 13:12:13.275631	\N
7642	187	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:13.367383	2025-07-06 13:12:13.367387	\N
7643	188	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:13.459375	2025-07-06 13:12:13.459377	\N
7644	175	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:13.878797	2025-07-06 13:12:13.878801	\N
7645	178	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:13.973062	2025-07-06 13:12:13.973066	\N
7646	180	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.064841	2025-07-06 13:12:14.064846	\N
7647	182	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.156706	2025-07-06 13:12:14.156711	\N
7648	173	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.248308	2025-07-06 13:12:14.248313	\N
7649	172	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.340372	2025-07-06 13:12:14.340378	\N
7650	171	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.432645	2025-07-06 13:12:14.432649	\N
7651	174	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.525629	2025-07-06 13:12:14.525634	\N
7652	177	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.618237	2025-07-06 13:12:14.618241	\N
7653	169	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.710094	2025-07-06 13:12:14.710098	\N
7654	183	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.802598	2025-07-06 13:12:14.802603	\N
7655	181	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.894264	2025-07-06 13:12:14.894269	\N
7656	179	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:14.986017	2025-07-06 13:12:14.986022	\N
7657	226	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:15.079251	2025-07-06 13:12:15.079255	\N
7658	227	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:15.171121	2025-07-06 13:12:15.171124	\N
7659	193	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:15.583177	2025-07-06 13:12:15.583182	\N
7660	190	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:15.675297	2025-07-06 13:12:15.675303	\N
7661	192	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:15.768604	2025-07-06 13:12:15.76861	\N
7662	191	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:15.861121	2025-07-06 13:12:15.861125	\N
7663	189	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:15.953254	2025-07-06 13:12:15.953257	\N
7664	214	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:16.364339	2025-07-06 13:12:16.364343	\N
7665	194	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:16.456017	2025-07-06 13:12:16.45602	\N
7666	195	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:16.549318	2025-07-06 13:12:16.549323	\N
7667	196	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:16.641665	2025-07-06 13:12:16.641669	\N
7668	197	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:16.733482	2025-07-06 13:12:16.733487	\N
7669	200	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:16.825292	2025-07-06 13:12:16.825297	\N
7670	202	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:16.917115	2025-07-06 13:12:16.917119	\N
7671	203	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.00867	2025-07-06 13:12:17.008674	\N
7672	205	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.101279	2025-07-06 13:12:17.101283	\N
7673	206	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.195827	2025-07-06 13:12:17.195832	\N
7674	207	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.288377	2025-07-06 13:12:17.288381	\N
7675	208	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.379916	2025-07-06 13:12:17.379935	\N
2897	194	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:03.985283	2025-04-23 13:37:03.985287	1
2898	195	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:04.073029	2025-04-23 13:37:04.073034	1
2899	196	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:04.159816	2025-04-23 13:37:04.15982	1
7676	209	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.474727	2025-07-06 13:12:17.474731	\N
7677	198	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.569797	2025-07-06 13:12:17.569801	\N
7678	201	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.666013	2025-07-06 13:12:17.666018	\N
7679	204	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.758547	2025-07-06 13:12:17.758551	\N
7680	225	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.850808	2025-07-06 13:12:17.850814	\N
7681	230	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:17.942531	2025-07-06 13:12:17.942534	\N
7682	231	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:18.034941	2025-07-06 13:12:18.034944	\N
7683	216	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:18.44636	2025-07-06 13:12:18.446365	\N
7684	217	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:18.540334	2025-07-06 13:12:18.540338	\N
7685	218	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:18.632911	2025-07-06 13:12:18.632916	\N
7686	219	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:18.725239	2025-07-06 13:12:18.725245	\N
7687	220	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:18.817026	2025-07-06 13:12:18.81703	\N
7688	221	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:18.909309	2025-07-06 13:12:18.909313	\N
7689	222	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:19.025791	2025-07-06 13:12:19.025793	\N
7690	223	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:19.436658	2025-07-06 13:12:19.436664	\N
7691	224	2025-07-06	\N	\N	present	\N	2025-07-06 13:12:19.52866	2025-07-06 13:12:19.528663	\N
7692	186	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:24.412901	2025-07-06 13:12:24.412907	\N
7693	184	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:24.50537	2025-07-06 13:12:24.505376	\N
7694	185	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:24.597885	2025-07-06 13:12:24.597889	\N
7695	187	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:24.690783	2025-07-06 13:12:24.690787	\N
7696	188	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:24.783114	2025-07-06 13:12:24.783118	\N
7697	186	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:24.877408	2025-07-06 13:12:24.877412	\N
7698	184	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:24.970025	2025-07-06 13:12:24.970029	\N
7699	185	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:25.061901	2025-07-06 13:12:25.061905	\N
7700	187	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:25.154026	2025-07-06 13:12:25.154031	\N
7701	188	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:25.246114	2025-07-06 13:12:25.246117	\N
7702	175	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:27.985812	2025-07-06 13:12:27.985817	\N
7703	178	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.077272	2025-07-06 13:12:28.077276	\N
7704	180	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.169169	2025-07-06 13:12:28.169174	\N
7705	182	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.261497	2025-07-06 13:12:28.261501	\N
7706	173	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.355364	2025-07-06 13:12:28.355369	\N
7707	172	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.447122	2025-07-06 13:12:28.447126	\N
7708	171	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.538629	2025-07-06 13:12:28.538633	\N
7709	174	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.630307	2025-07-06 13:12:28.630312	\N
7710	177	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.722348	2025-07-06 13:12:28.722353	\N
7711	169	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.814142	2025-07-06 13:12:28.814146	\N
7712	183	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.905647	2025-07-06 13:12:28.905653	\N
7713	181	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:28.998478	2025-07-06 13:12:28.998483	\N
7714	179	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:29.090236	2025-07-06 13:12:29.09024	\N
7715	226	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:29.182006	2025-07-06 13:12:29.182011	\N
7716	227	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:29.274081	2025-07-06 13:12:29.274085	\N
7717	175	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:29.365648	2025-07-06 13:12:29.365652	\N
7718	178	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:29.457706	2025-07-06 13:12:29.45771	\N
7719	180	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:29.55418	2025-07-06 13:12:29.554184	\N
7720	182	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:29.646014	2025-07-06 13:12:29.646019	\N
7721	173	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:29.739642	2025-07-06 13:12:29.739648	\N
7722	172	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:29.832515	2025-07-06 13:12:29.83252	\N
7723	171	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:29.924269	2025-07-06 13:12:29.924273	\N
7724	174	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:30.016068	2025-07-06 13:12:30.016072	\N
7725	177	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:30.107515	2025-07-06 13:12:30.107519	\N
7726	169	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:30.199729	2025-07-06 13:12:30.199733	\N
7727	183	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:30.291698	2025-07-06 13:12:30.291702	\N
7728	181	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:30.384817	2025-07-06 13:12:30.384821	\N
7729	179	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:30.476532	2025-07-06 13:12:30.476537	\N
7730	226	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:30.568136	2025-07-06 13:12:30.56814	\N
7731	227	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:30.660489	2025-07-06 13:12:30.660492	\N
7732	193	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:32.460758	2025-07-06 13:12:32.460762	\N
7733	190	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:32.552275	2025-07-06 13:12:32.55228	\N
7734	192	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:32.645257	2025-07-06 13:12:32.64526	\N
7735	191	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:32.737474	2025-07-06 13:12:32.737478	\N
7736	189	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:32.833772	2025-07-06 13:12:32.833776	\N
7737	193	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:32.925216	2025-07-06 13:12:32.925221	\N
7738	190	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:33.017184	2025-07-06 13:12:33.017188	\N
7739	192	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:33.109357	2025-07-06 13:12:33.10936	\N
7740	191	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:33.20159	2025-07-06 13:12:33.201595	\N
7741	189	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:33.293061	2025-07-06 13:12:33.293067	\N
7742	214	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:36.569025	2025-07-06 13:12:36.569031	\N
7743	194	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:36.661965	2025-07-06 13:12:36.66197	\N
7744	195	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:36.754343	2025-07-06 13:12:36.754348	\N
7745	196	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:36.847408	2025-07-06 13:12:36.847413	\N
7746	197	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:36.940693	2025-07-06 13:12:36.940701	\N
7747	200	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.032521	2025-07-06 13:12:37.032526	\N
7748	202	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.124678	2025-07-06 13:12:37.124698	\N
7749	203	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.216707	2025-07-06 13:12:37.216712	\N
7750	205	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.309057	2025-07-06 13:12:37.309061	\N
7751	206	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.409351	2025-07-06 13:12:37.409356	\N
7752	207	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.501647	2025-07-06 13:12:37.501651	\N
7753	208	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.593551	2025-07-06 13:12:37.593555	\N
7754	209	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.685698	2025-07-06 13:12:37.685704	\N
7755	198	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.777409	2025-07-06 13:12:37.777413	\N
7756	201	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.872071	2025-07-06 13:12:37.872076	\N
7757	204	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:37.965907	2025-07-06 13:12:37.965912	\N
7758	225	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:38.057831	2025-07-06 13:12:38.057835	\N
7759	230	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:38.154682	2025-07-06 13:12:38.154687	\N
7760	231	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:38.247011	2025-07-06 13:12:38.247016	\N
7761	214	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:38.339113	2025-07-06 13:12:38.339117	\N
7762	194	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:38.433152	2025-07-06 13:12:38.433157	\N
7763	195	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:38.525506	2025-07-06 13:12:38.525509	\N
7764	196	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:38.617241	2025-07-06 13:12:38.617245	\N
7765	197	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:38.709267	2025-07-06 13:12:38.70927	\N
7766	200	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:38.802489	2025-07-06 13:12:38.802495	\N
7767	202	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:38.900048	2025-07-06 13:12:38.900053	\N
7768	203	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:38.991973	2025-07-06 13:12:38.991977	\N
7769	205	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:39.083545	2025-07-06 13:12:39.083549	\N
7770	206	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:39.175834	2025-07-06 13:12:39.175839	\N
7771	207	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:39.268273	2025-07-06 13:12:39.268277	\N
7772	208	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:39.365682	2025-07-06 13:12:39.36569	\N
7773	209	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:39.459649	2025-07-06 13:12:39.459653	\N
7774	198	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:39.551529	2025-07-06 13:12:39.551533	\N
7775	201	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:39.643898	2025-07-06 13:12:39.643901	\N
7776	204	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:39.735251	2025-07-06 13:12:39.735254	\N
7777	225	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:39.828535	2025-07-06 13:12:39.828539	\N
7778	230	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:39.920151	2025-07-06 13:12:39.920155	\N
3002	216	2025-04-13	\N	\N	present	\N	2025-04-23 13:40:29.498939	2025-04-23 13:40:29.498946	1
3003	217	2025-04-13	\N	\N	present	\N	2025-04-23 13:40:29.59107	2025-04-23 13:40:29.591077	1
3004	218	2025-04-13	\N	\N	present	\N	2025-04-23 13:40:29.678086	2025-04-23 13:40:29.678092	1
7779	231	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:40.012262	2025-07-06 13:12:40.012266	\N
7780	216	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:42.33966	2025-07-06 13:12:42.339665	\N
7781	217	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:42.431808	2025-07-06 13:12:42.431812	\N
7782	218	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:42.523777	2025-07-06 13:12:42.523782	\N
7783	219	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:42.615382	2025-07-06 13:12:42.615386	\N
7784	220	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:42.707389	2025-07-06 13:12:42.707395	\N
7785	221	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:42.799347	2025-07-06 13:12:42.799352	\N
7786	222	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:42.893993	2025-07-06 13:12:42.893998	\N
7787	216	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:42.989952	2025-07-06 13:12:42.989956	\N
7788	217	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:43.083859	2025-07-06 13:12:43.083863	\N
7789	218	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:43.175905	2025-07-06 13:12:43.17591	\N
7790	219	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:43.268102	2025-07-06 13:12:43.268106	\N
7791	220	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:43.360924	2025-07-06 13:12:43.360929	\N
7792	221	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:43.452928	2025-07-06 13:12:43.452939	\N
7793	222	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:43.545522	2025-07-06 13:12:43.545527	\N
7794	223	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:44.56293	2025-07-06 13:12:44.562934	\N
7795	224	2025-07-04	\N	\N	present	\N	2025-07-06 13:12:44.654748	2025-07-06 13:12:44.654752	\N
7796	223	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:44.746721	2025-07-06 13:12:44.746726	\N
7797	224	2025-07-05	\N	\N	present	\N	2025-07-06 13:12:44.839014	2025-07-06 13:12:44.839018	\N
3109	198	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:16.711157	2025-04-24 19:06:16.711161	1
3111	200	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:16.895478	2025-04-24 19:06:16.895482	1
3112	201	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:16.987258	2025-04-24 19:06:16.987263	1
3113	202	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:17.079119	2025-04-24 19:06:17.079125	1
3114	203	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:17.172023	2025-04-24 19:06:17.172028	1
3115	204	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:17.263805	2025-04-24 19:06:17.26381	1
3116	205	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:17.355588	2025-04-24 19:06:17.355593	1
3117	206	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:17.454561	2025-04-24 19:06:17.454566	1
3118	207	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:17.547379	2025-04-24 19:06:17.547383	1
3119	208	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:17.644974	2025-04-24 19:06:17.644979	1
3216	185	2025-04-27	\N	\N	present	\N	2025-04-27 10:24:51.433449	2025-04-27 10:24:51.433454	1
3217	186	2025-04-27	\N	\N	present	\N	2025-04-27 10:24:51.520751	2025-04-27 10:24:51.520757	1
3218	187	2025-04-27	\N	\N	present	\N	2025-04-27 10:24:51.611729	2025-04-27 10:24:51.611734	1
3219	188	2025-04-27	\N	\N	present	\N	2025-04-27 10:24:51.698618	2025-04-27 10:24:51.698623	1
3220	180	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:27.523986	2025-04-27 10:25:27.523991	1
3221	181	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:27.609895	2025-04-27 10:25:27.609901	1
3222	179	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:27.696651	2025-04-27 10:25:27.696656	1
3223	178	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:27.78271	2025-04-27 10:25:27.782715	1
3224	183	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:27.868507	2025-04-27 10:25:27.868513	1
3225	182	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:27.954289	2025-04-27 10:25:27.954294	1
3323	221	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:35.668096	2025-04-28 08:49:35.6681	1
3324	222	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:35.755365	2025-04-28 08:49:35.75537	1
3325	184	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:22.495821	2025-04-29 22:11:22.495824	1
3326	185	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:22.594907	2025-04-29 22:11:22.594912	1
3327	186	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:22.685265	2025-04-29 22:11:22.685269	1
3328	187	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:22.778211	2025-04-29 22:11:22.778214	1
3329	188	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:22.874137	2025-04-29 22:11:22.874141	1
3330	180	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:39.133277	2025-04-29 22:11:39.133281	1
3331	181	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:39.222585	2025-04-29 22:11:39.222589	1
3430	220	2025-04-30	\N	\N	present	\N	2025-04-30 10:35:09.599315	2025-04-30 10:35:09.599319	1
3431	221	2025-04-30	\N	\N	present	\N	2025-04-30 10:35:09.689282	2025-04-30 10:35:09.689287	1
3432	222	2025-04-30	\N	\N	present	\N	2025-04-30 10:35:09.78056	2025-04-30 10:35:09.780565	1
3433	184	2025-05-01	\N	\N	present	\N	2025-05-08 19:08:37.585817	2025-05-08 19:08:37.585822	1
3434	185	2025-05-01	\N	\N	present	\N	2025-05-08 19:08:37.683363	2025-05-08 19:08:37.683368	1
3435	186	2025-05-01	\N	\N	present	\N	2025-05-08 19:08:37.77388	2025-05-08 19:08:37.773885	1
3436	187	2025-05-01	\N	\N	present	\N	2025-05-08 19:08:37.86514	2025-05-08 19:08:37.865145	1
3537	183	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:14.85668	2025-05-08 19:09:14.856684	1
3538	182	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:14.947251	2025-05-08 19:09:14.947255	1
3539	175	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:15.036665	2025-05-08 19:09:15.036669	1
3540	173	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:15.126816	2025-05-08 19:09:15.126821	1
3541	172	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:15.217301	2025-05-08 19:09:15.217305	1
3543	171	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:15.39654	2025-05-08 19:09:15.396544	1
3544	174	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:15.485903	2025-05-08 19:09:15.485907	1
3545	177	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:15.576109	2025-05-08 19:09:15.576114	1
3644	208	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:49.006332	2025-05-08 19:11:49.006336	1
3645	209	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:49.095795	2025-05-08 19:11:49.095799	1
3646	210	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:49.185336	2025-05-08 19:11:49.18534	1
3647	198	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:49.276178	2025-05-08 19:11:49.276183	1
3648	201	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:49.366383	2025-05-08 19:11:49.366388	1
3649	204	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:49.456309	2025-05-08 19:11:49.456313	1
3651	212	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:49.665135	2025-05-08 19:11:49.665139	1
3652	214	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:49.77904	2025-05-08 19:11:49.779044	1
3653	211	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:49.868868	2025-05-08 19:11:49.868872	1
3751	210	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:58.879383	2025-05-08 19:11:58.879387	1
3752	198	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:58.970825	2025-05-08 19:11:58.97083	1
3753	201	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:59.060279	2025-05-08 19:11:59.060283	1
3754	204	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:59.149328	2025-05-08 19:11:59.149333	1
3858	185	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:00.754103	2025-05-09 10:59:00.754108	1
3859	186	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:00.841779	2025-05-09 10:59:00.841784	1
3860	187	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:00.928571	2025-05-09 10:59:00.928575	1
3861	188	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:01.016303	2025-05-09 10:59:01.016308	1
3862	180	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:13.336988	2025-05-09 10:59:13.336993	1
3863	181	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:13.423423	2025-05-09 10:59:13.423428	1
3864	179	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:13.509924	2025-05-09 10:59:13.509929	1
3965	186	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:20.82865	2025-05-12 11:52:20.828655	1
3966	187	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:20.916936	2025-05-12 11:52:20.916941	1
3967	188	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:21.056877	2025-05-12 11:52:21.056881	1
3968	184	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:21.143748	2025-05-12 11:52:21.143753	1
3969	185	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:21.23121	2025-05-12 11:52:21.231215	1
4119	184	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:17.203071	2025-05-13 21:36:17.203076	1
4120	185	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:17.290952	2025-05-13 21:36:17.290957	1
4121	186	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:17.376584	2025-05-13 21:36:17.376589	1
4122	187	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:17.468701	2025-05-13 21:36:17.468706	1
4123	188	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:17.555366	2025-05-13 21:36:17.55537	1
4124	180	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.00532	2025-05-13 21:36:26.005324	1
4125	181	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.090513	2025-05-13 21:36:26.090518	1
4126	179	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.175366	2025-05-13 21:36:26.175371	1
4127	178	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.260867	2025-05-13 21:36:26.260871	1
4128	183	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.345438	2025-05-13 21:36:26.345442	1
4129	182	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.429812	2025-05-13 21:36:26.429816	1
4130	175	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.515195	2025-05-13 21:36:26.515199	1
4131	173	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.600835	2025-05-13 21:36:26.60084	1
4132	172	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.686907	2025-05-13 21:36:26.686912	1
4134	171	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.858291	2025-05-13 21:36:26.858296	1
4135	174	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:26.946187	2025-05-13 21:36:26.946192	1
4136	177	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:27.030693	2025-05-13 21:36:27.030698	1
4137	169	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:27.115547	2025-05-13 21:36:27.115553	1
4139	193	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:30.171304	2025-05-13 21:36:30.171308	1
4140	191	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:30.257007	2025-05-13 21:36:30.257011	1
4141	189	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:30.341809	2025-05-13 21:36:30.341813	1
4142	190	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:30.426259	2025-05-13 21:36:30.426264	1
4143	192	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:30.512351	2025-05-13 21:36:30.512355	1
4144	194	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:41.823115	2025-05-13 21:36:41.82312	1
4145	195	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:41.909588	2025-05-13 21:36:41.909593	1
4146	196	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:41.99441	2025-05-13 21:36:41.994414	1
4147	197	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.079756	2025-05-13 21:36:42.079761	1
4148	200	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.165369	2025-05-13 21:36:42.165373	1
4149	202	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.251089	2025-05-13 21:36:42.251093	1
4150	203	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.337171	2025-05-13 21:36:42.337175	1
4151	205	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.422276	2025-05-13 21:36:42.42228	1
4152	206	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.507507	2025-05-13 21:36:42.507512	1
4153	207	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.592369	2025-05-13 21:36:42.592373	1
4154	208	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.678694	2025-05-13 21:36:42.678698	1
4155	209	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.764714	2025-05-13 21:36:42.764718	1
4156	210	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.854316	2025-05-13 21:36:42.85432	1
4157	198	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:42.947827	2025-05-13 21:36:42.947832	1
4158	201	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:43.04613	2025-05-13 21:36:43.046135	1
4183	224	2025-05-10	\N	\N	present	\N	2025-05-13 21:52:11.285142	2025-05-13 21:52:11.285145	1
4718	191	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:54.030968	2025-05-23 13:54:54.030973	1
5037	197	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:29.663125	2025-05-29 10:25:29.66313	1
6319	174	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:42.46273	2025-06-11 13:35:42.462734	1
6320	177	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:42.555101	2025-06-11 13:35:42.555106	1
6321	169	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:42.647439	2025-06-11 13:35:42.647444	1
6322	183	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:42.739536	2025-06-11 13:35:42.739541	1
6323	181	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:42.837214	2025-06-11 13:35:42.837218	1
6325	226	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:43.02372	2025-06-11 13:35:43.023725	1
6326	227	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:43.115263	2025-06-11 13:35:43.115265	1
6327	193	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:45.643889	2025-06-11 13:35:45.643894	1
6328	191	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:45.735673	2025-06-11 13:35:45.735678	1
6329	189	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:45.8283	2025-06-11 13:35:45.828305	1
6330	190	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:45.921117	2025-06-11 13:35:45.921122	1
6331	192	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:46.013182	2025-06-11 13:35:46.013186	1
6332	193	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:46.104657	2025-06-11 13:35:46.104662	1
6333	191	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:46.19617	2025-06-11 13:35:46.196174	1
6334	189	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:46.288158	2025-06-11 13:35:46.288162	1
6335	190	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:46.380988	2025-06-11 13:35:46.380993	1
6336	192	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:46.472581	2025-06-11 13:35:46.472583	1
6337	194	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:54.981351	2025-06-11 13:35:54.981355	1
6338	195	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:55.073645	2025-06-11 13:35:55.07365	1
6339	196	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:55.255418	2025-06-11 13:35:55.255424	1
6340	197	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:55.348572	2025-06-11 13:35:55.348578	1
6341	200	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:55.440423	2025-06-11 13:35:55.440428	1
6342	202	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:55.531848	2025-06-11 13:35:55.531852	1
6343	203	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:55.628859	2025-06-11 13:35:55.628864	1
6344	205	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:55.723619	2025-06-11 13:35:55.723624	1
6656	204	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:34.164559	2025-06-15 08:23:34.164563	1
477	180	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:16.226326	2025-04-21 19:35:16.22633	1
478	181	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:16.311061	2025-04-21 19:35:16.311064	1
479	179	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:16.39499	2025-04-21 19:35:16.394993	1
480	178	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:16.478902	2025-04-21 19:35:16.478906	1
481	183	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:16.562538	2025-04-21 19:35:16.562541	1
482	182	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:16.643872	2025-04-21 19:35:16.643876	1
483	175	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:16.725883	2025-04-21 19:35:16.725886	1
484	173	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:16.81151	2025-04-21 19:35:16.811514	1
485	172	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:16.893152	2025-04-21 19:35:16.893156	1
487	171	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:17.063255	2025-04-21 19:35:17.063259	1
488	174	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:17.146227	2025-04-21 19:35:17.146232	1
489	177	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:17.227875	2025-04-21 19:35:17.227879	1
490	169	2025-04-01	\N	\N	present	\N	2025-04-21 19:35:17.315231	2025-04-21 19:35:17.315234	1
494	180	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:42.698921	2025-04-21 19:35:42.698924	1
495	181	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:42.783706	2025-04-21 19:35:42.78371	1
496	179	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:42.870395	2025-04-21 19:35:42.8704	1
497	178	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:42.956108	2025-04-21 19:35:42.956112	1
498	183	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:43.040156	2025-04-21 19:35:43.040159	1
499	182	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:43.124292	2025-04-21 19:35:43.124296	1
500	175	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:43.209622	2025-04-21 19:35:43.209627	1
501	173	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:43.308228	2025-04-21 19:35:43.308232	1
502	172	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:43.391137	2025-04-21 19:35:43.39114	1
504	171	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:43.561186	2025-04-21 19:35:43.56119	1
505	174	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:43.643017	2025-04-21 19:35:43.64302	1
506	177	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:43.735005	2025-04-21 19:35:43.735009	1
507	169	2025-04-02	\N	\N	present	\N	2025-04-21 19:35:43.828472	2025-04-21 19:35:43.828483	1
511	180	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:25.265167	2025-04-21 19:37:25.265171	1
512	181	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:25.348071	2025-04-21 19:37:25.348075	1
513	179	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:25.429622	2025-04-21 19:37:25.429625	1
514	178	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:25.512314	2025-04-21 19:37:25.512319	1
515	183	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:25.595093	2025-04-21 19:37:25.595097	1
516	182	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:25.677752	2025-04-21 19:37:25.677756	1
517	175	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:25.762071	2025-04-21 19:37:25.762075	1
518	173	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:25.846534	2025-04-21 19:37:25.846537	1
519	172	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:25.929152	2025-04-21 19:37:25.929156	1
521	171	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:26.09037	2025-04-21 19:37:26.090374	1
522	174	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:26.172563	2025-04-21 19:37:26.172568	1
523	177	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:26.253882	2025-04-21 19:37:26.253885	1
524	169	2025-04-03	\N	\N	present	\N	2025-04-21 19:37:26.334762	2025-04-21 19:37:26.334767	1
528	180	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:45.90237	2025-04-21 19:37:45.902373	1
529	181	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:45.986524	2025-04-21 19:37:45.986526	1
530	179	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:46.069551	2025-04-21 19:37:46.069555	1
531	178	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:46.152099	2025-04-21 19:37:46.152103	1
532	183	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:46.234284	2025-04-21 19:37:46.234288	1
533	182	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:46.319259	2025-04-21 19:37:46.319264	1
534	175	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:46.457726	2025-04-21 19:37:46.45773	1
535	173	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:46.541525	2025-04-21 19:37:46.541529	1
536	172	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:46.626181	2025-04-21 19:37:46.626186	1
538	171	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:46.802335	2025-04-21 19:37:46.802338	1
539	174	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:46.884561	2025-04-21 19:37:46.884565	1
540	177	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:46.96764	2025-04-21 19:37:46.967644	1
541	169	2025-04-05	\N	\N	present	\N	2025-04-21 19:37:47.052476	2025-04-21 19:37:47.05248	1
544	181	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:53.237886	2025-04-21 23:10:53.23789	1
545	179	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:53.331576	2025-04-21 23:10:53.331581	1
546	178	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:53.422644	2025-04-21 23:10:53.422649	1
547	183	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:53.515853	2025-04-21 23:10:53.515858	1
548	182	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:53.606604	2025-04-21 23:10:53.606611	1
549	175	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:53.69954	2025-04-21 23:10:53.699545	1
550	173	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:53.790509	2025-04-21 23:10:53.790514	1
551	172	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:53.881739	2025-04-21 23:10:53.881744	1
553	171	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:54.065642	2025-04-21 23:10:54.065646	1
554	174	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:54.157102	2025-04-21 23:10:54.157106	1
555	177	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:54.247805	2025-04-21 23:10:54.24781	1
556	169	2025-04-21	\N	\N	present	\N	2025-04-21 23:10:54.339633	2025-04-21 23:10:54.339637	1
559	180	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:41.211885	2025-04-21 23:15:41.21189	1
560	181	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:41.303281	2025-04-21 23:15:41.303286	1
561	179	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:41.393996	2025-04-21 23:15:41.394001	1
562	178	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:41.484904	2025-04-21 23:15:41.484908	1
563	183	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:41.575735	2025-04-21 23:15:41.57574	1
564	182	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:41.666643	2025-04-21 23:15:41.666648	1
565	175	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:41.757373	2025-04-21 23:15:41.757378	1
566	173	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:41.848248	2025-04-21 23:15:41.848253	1
567	172	2025-04-06	\N	\N	present	\N	2025-04-21 23:15:41.94021	2025-04-21 23:15:41.940215	1
582	173	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:10.200711	2025-04-21 23:16:10.200724	1
583	172	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:10.296543	2025-04-21 23:16:10.296549	1
585	171	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:10.486671	2025-04-21 23:16:10.486677	1
586	174	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:10.580222	2025-04-21 23:16:10.580228	1
587	177	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:10.682297	2025-04-21 23:16:10.682303	1
588	169	2025-04-07	\N	\N	present	\N	2025-04-21 23:16:10.777275	2025-04-21 23:16:10.777279	1
591	180	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:56.233523	2025-04-21 23:24:56.233528	1
592	181	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:56.322621	2025-04-21 23:24:56.322626	1
593	179	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:56.410496	2025-04-21 23:24:56.410501	1
594	178	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:56.498852	2025-04-21 23:24:56.498857	1
595	183	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:56.587207	2025-04-21 23:24:56.587212	1
596	182	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:56.674946	2025-04-21 23:24:56.674951	1
597	175	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:56.762351	2025-04-21 23:24:56.762355	1
598	173	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:56.853573	2025-04-21 23:24:56.853579	1
599	172	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:56.942375	2025-04-21 23:24:56.94238	1
601	171	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:57.11706	2025-04-21 23:24:57.117065	1
602	174	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:57.204433	2025-04-21 23:24:57.204438	1
603	177	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:57.291178	2025-04-21 23:24:57.291183	1
604	169	2025-04-08	\N	\N	present	\N	2025-04-21 23:24:57.377793	2025-04-21 23:24:57.377798	1
607	180	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:12.044914	2025-04-21 23:25:12.044919	1
608	181	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:12.134086	2025-04-21 23:25:12.134091	1
609	179	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:12.224478	2025-04-21 23:25:12.224483	1
610	178	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:12.311397	2025-04-21 23:25:12.311402	1
611	183	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:12.3995	2025-04-21 23:25:12.399506	1
612	182	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:12.489999	2025-04-21 23:25:12.490003	1
613	175	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:12.577377	2025-04-21 23:25:12.577381	1
614	173	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:12.66604	2025-04-21 23:25:12.666045	1
615	172	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:12.753923	2025-04-21 23:25:12.753928	1
617	171	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:12.932701	2025-04-21 23:25:12.932706	1
618	174	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:13.02251	2025-04-21 23:25:13.022516	1
619	177	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:13.109675	2025-04-21 23:25:13.10968	1
620	169	2025-04-09	\N	\N	present	\N	2025-04-21 23:25:13.196526	2025-04-21 23:25:13.196531	1
623	180	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:44.443454	2025-04-21 23:25:44.443465	1
624	181	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:44.541295	2025-04-21 23:25:44.541306	1
625	179	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:44.640203	2025-04-21 23:25:44.640216	1
626	178	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:44.741446	2025-04-21 23:25:44.741464	1
627	183	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:44.837128	2025-04-21 23:25:44.837146	1
628	182	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:44.93712	2025-04-21 23:25:44.937131	1
629	175	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:45.034651	2025-04-21 23:25:45.034664	1
630	173	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:45.128266	2025-04-21 23:25:45.128278	1
631	172	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:45.220549	2025-04-21 23:25:45.220562	1
633	171	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:45.423732	2025-04-21 23:25:45.423742	1
634	174	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:45.517759	2025-04-21 23:25:45.517772	1
635	177	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:45.608991	2025-04-21 23:25:45.608998	1
636	169	2025-04-10	\N	\N	present	\N	2025-04-21 23:25:45.697281	2025-04-21 23:25:45.697288	1
639	180	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:10.954545	2025-04-21 23:26:10.95455	1
640	181	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:11.042833	2025-04-21 23:26:11.04284	1
641	179	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:11.133576	2025-04-21 23:26:11.133581	1
642	178	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:11.221002	2025-04-21 23:26:11.221007	1
643	183	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:11.30861	2025-04-21 23:26:11.308615	1
644	182	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:11.397203	2025-04-21 23:26:11.397208	1
645	175	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:11.485254	2025-04-21 23:26:11.485259	1
646	173	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:11.579148	2025-04-21 23:26:11.579154	1
647	172	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:11.671731	2025-04-21 23:26:11.671736	1
649	171	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:11.847944	2025-04-21 23:26:11.847949	1
650	174	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:11.94234	2025-04-21 23:26:11.942344	1
651	177	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:12.029596	2025-04-21 23:26:12.0296	1
652	169	2025-04-11	\N	\N	present	\N	2025-04-21 23:26:12.122099	2025-04-21 23:26:12.122104	1
655	180	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:49.1672	2025-04-21 23:27:49.167211	1
656	181	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:49.261499	2025-04-21 23:27:49.261511	1
657	179	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:49.353939	2025-04-21 23:27:49.353949	1
658	178	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:49.445138	2025-04-21 23:27:49.445147	1
659	183	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:49.538164	2025-04-21 23:27:49.538172	1
660	182	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:49.629956	2025-04-21 23:27:49.629967	1
661	175	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:49.726957	2025-04-21 23:27:49.726969	1
662	173	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:49.817111	2025-04-21 23:27:49.81712	1
663	172	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:49.911377	2025-04-21 23:27:49.911388	1
665	171	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:50.092402	2025-04-21 23:27:50.092412	1
666	174	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:50.183423	2025-04-21 23:27:50.183432	1
667	177	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:50.280977	2025-04-21 23:27:50.280984	1
668	169	2025-04-12	\N	\N	present	\N	2025-04-21 23:27:50.371418	2025-04-21 23:27:50.371428	1
671	180	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:22.363713	2025-04-21 23:28:22.363719	1
672	181	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:22.452757	2025-04-21 23:28:22.452763	1
673	179	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:22.540847	2025-04-21 23:28:22.540854	1
674	178	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:22.63038	2025-04-21 23:28:22.630387	1
675	183	2025-04-13	\N	\N	present	\N	2025-04-21 23:28:22.718504	2025-04-21 23:28:22.71851	1
691	183	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:10.905832	2025-04-21 23:30:10.905837	1
692	182	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:10.997572	2025-04-21 23:30:10.997616	1
693	175	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:11.084532	2025-04-21 23:30:11.084536	1
694	173	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:11.171692	2025-04-21 23:30:11.171696	1
695	172	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:11.258844	2025-04-21 23:30:11.258849	1
697	171	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:11.43622	2025-04-21 23:30:11.436225	1
698	174	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:11.524373	2025-04-21 23:30:11.524377	1
699	177	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:11.610806	2025-04-21 23:30:11.610812	1
700	169	2025-04-14	\N	\N	present	\N	2025-04-21 23:30:11.700994	2025-04-21 23:30:11.700999	1
703	180	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:52.433373	2025-04-21 23:30:52.433379	1
704	181	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:52.520865	2025-04-21 23:30:52.520878	1
705	179	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:52.608687	2025-04-21 23:30:52.608693	1
706	178	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:52.695119	2025-04-21 23:30:52.695124	1
707	183	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:52.781411	2025-04-21 23:30:52.781417	1
708	182	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:52.870841	2025-04-21 23:30:52.870847	1
709	175	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:52.957575	2025-04-21 23:30:52.957595	1
710	173	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:53.045253	2025-04-21 23:30:53.045259	1
711	172	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:53.132687	2025-04-21 23:30:53.132694	1
713	171	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:53.308478	2025-04-21 23:30:53.308483	1
714	174	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:53.396048	2025-04-21 23:30:53.396053	1
715	177	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:53.484459	2025-04-21 23:30:53.484465	1
716	169	2025-04-15	\N	\N	present	\N	2025-04-21 23:30:53.571212	2025-04-21 23:30:53.571217	1
719	180	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:14.356234	2025-04-21 23:34:14.356243	1
720	181	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:14.44834	2025-04-21 23:34:14.448349	1
721	179	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:14.543507	2025-04-21 23:34:14.543516	1
722	178	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:14.638547	2025-04-21 23:34:14.63857	1
723	183	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:14.73442	2025-04-21 23:34:14.734431	1
724	182	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:14.827747	2025-04-21 23:34:14.827755	1
725	175	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:14.921625	2025-04-21 23:34:14.921636	1
726	173	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:15.016911	2025-04-21 23:34:15.016921	1
727	172	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:15.107693	2025-04-21 23:34:15.107699	1
729	171	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:15.29532	2025-04-21 23:34:15.29533	1
730	174	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:15.388067	2025-04-21 23:34:15.388077	1
731	177	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:15.480294	2025-04-21 23:34:15.480303	1
732	169	2025-04-16	\N	\N	present	\N	2025-04-21 23:34:15.572403	2025-04-21 23:34:15.572414	1
735	180	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:31.842017	2025-04-21 23:34:31.842022	1
736	181	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:31.930259	2025-04-21 23:34:31.930264	1
737	179	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.015694	2025-04-21 23:34:32.015699	1
738	178	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.100754	2025-04-21 23:34:32.100758	1
739	183	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.18974	2025-04-21 23:34:32.189745	1
740	182	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.277803	2025-04-21 23:34:32.277808	1
741	175	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.363413	2025-04-21 23:34:32.363418	1
742	173	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.449279	2025-04-21 23:34:32.449283	1
743	172	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.534829	2025-04-21 23:34:32.534834	1
745	171	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.706226	2025-04-21 23:34:32.706231	1
746	174	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.79247	2025-04-21 23:34:32.792475	1
747	177	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.894737	2025-04-21 23:34:32.894742	1
748	169	2025-04-17	\N	\N	present	\N	2025-04-21 23:34:32.980278	2025-04-21 23:34:32.980284	1
751	180	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:53.317679	2025-04-21 23:34:53.317684	1
752	181	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:53.402755	2025-04-21 23:34:53.40276	1
753	179	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:53.488767	2025-04-21 23:34:53.488772	1
754	178	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:53.578254	2025-04-21 23:34:53.578259	1
755	183	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:53.664007	2025-04-21 23:34:53.664012	1
756	182	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:53.749965	2025-04-21 23:34:53.749971	1
757	175	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:53.83552	2025-04-21 23:34:53.835524	1
758	173	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:53.926193	2025-04-21 23:34:53.926198	1
759	172	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:54.01438	2025-04-21 23:34:54.014385	1
761	171	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:54.196364	2025-04-21 23:34:54.19637	1
762	174	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:54.281826	2025-04-21 23:34:54.28183	1
763	177	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:54.367352	2025-04-21 23:34:54.367357	1
764	169	2025-04-18	\N	\N	present	\N	2025-04-21 23:34:54.45257	2025-04-21 23:34:54.452576	1
767	180	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:18.145993	2025-04-21 23:35:18.145997	1
768	181	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:18.231357	2025-04-21 23:35:18.231362	1
769	179	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:18.318407	2025-04-21 23:35:18.318411	1
770	178	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:18.403666	2025-04-21 23:35:18.403671	1
771	183	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:18.488896	2025-04-21 23:35:18.4889	1
772	182	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:18.574757	2025-04-21 23:35:18.574762	1
773	175	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:18.6604	2025-04-21 23:35:18.660405	1
774	173	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:18.746745	2025-04-21 23:35:18.74675	1
775	172	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:18.832497	2025-04-21 23:35:18.832502	1
777	171	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:19.003857	2025-04-21 23:35:19.003862	1
778	174	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:19.089099	2025-04-21 23:35:19.089103	1
779	177	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:19.174289	2025-04-21 23:35:19.174293	1
780	169	2025-04-19	\N	\N	present	\N	2025-04-21 23:35:19.260467	2025-04-21 23:35:19.260472	1
786	178	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:42.618684	2025-04-21 23:36:42.618689	1
787	183	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:42.704954	2025-04-21 23:36:42.704959	1
788	182	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:42.792003	2025-04-21 23:36:42.792008	1
789	175	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:42.881089	2025-04-21 23:36:42.881096	1
790	173	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:42.967754	2025-04-21 23:36:42.967759	1
791	172	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:43.054053	2025-04-21 23:36:43.054058	1
793	171	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:43.227302	2025-04-21 23:36:43.227308	1
794	174	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:43.314024	2025-04-21 23:36:43.314029	1
795	177	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:43.405368	2025-04-21 23:36:43.405374	1
796	169	2025-04-20	\N	\N	present	\N	2025-04-21 23:36:43.491741	2025-04-21 23:36:43.491746	1
800	184	2025-04-01	\N	\N	present	\N	2025-04-22 10:04:58.922124	2025-04-22 10:04:58.922129	1
801	185	2025-04-01	\N	\N	present	\N	2025-04-22 10:04:59.017793	2025-04-22 10:04:59.017798	1
802	186	2025-04-01	\N	\N	present	\N	2025-04-22 10:04:59.108528	2025-04-22 10:04:59.108533	1
803	187	2025-04-01	\N	\N	present	\N	2025-04-22 10:04:59.194868	2025-04-22 10:04:59.194872	1
804	188	2025-04-01	\N	\N	present	\N	2025-04-22 10:04:59.281314	2025-04-22 10:04:59.281319	1
805	184	2025-04-02	\N	\N	present	\N	2025-04-22 10:05:18.20816	2025-04-22 10:05:18.208165	1
806	185	2025-04-02	\N	\N	present	\N	2025-04-22 10:05:18.297029	2025-04-22 10:05:18.297034	1
807	186	2025-04-02	\N	\N	present	\N	2025-04-22 10:05:18.384709	2025-04-22 10:05:18.384715	1
808	187	2025-04-02	\N	\N	present	\N	2025-04-22 10:05:18.470282	2025-04-22 10:05:18.470287	1
809	188	2025-04-02	\N	\N	present	\N	2025-04-22 10:05:18.562966	2025-04-22 10:05:18.562971	1
810	184	2025-04-03	\N	\N	present	\N	2025-04-22 10:05:36.056486	2025-04-22 10:05:36.056491	1
811	185	2025-04-03	\N	\N	present	\N	2025-04-22 10:05:36.142038	2025-04-22 10:05:36.142044	1
812	186	2025-04-03	\N	\N	present	\N	2025-04-22 10:05:36.228016	2025-04-22 10:05:36.22802	1
813	187	2025-04-03	\N	\N	present	\N	2025-04-22 10:05:36.313855	2025-04-22 10:05:36.31386	1
814	188	2025-04-03	\N	\N	present	\N	2025-04-22 10:05:36.399327	2025-04-22 10:05:36.399332	1
815	184	2025-04-04	\N	\N	present	\N	2025-04-22 10:05:59.731856	2025-04-22 10:05:59.731861	1
816	185	2025-04-04	\N	\N	present	\N	2025-04-22 10:05:59.819149	2025-04-22 10:05:59.819154	1
817	186	2025-04-04	\N	\N	present	\N	2025-04-22 10:05:59.912153	2025-04-22 10:05:59.912158	1
818	187	2025-04-04	\N	\N	present	\N	2025-04-22 10:06:00.007209	2025-04-22 10:06:00.00723	1
819	188	2025-04-04	\N	\N	present	\N	2025-04-22 10:06:00.094388	2025-04-22 10:06:00.094393	1
820	184	2025-04-05	\N	\N	present	\N	2025-04-22 10:06:21.105698	2025-04-22 10:06:21.105703	1
821	185	2025-04-05	\N	\N	present	\N	2025-04-22 10:06:21.193957	2025-04-22 10:06:21.193963	1
822	186	2025-04-05	\N	\N	present	\N	2025-04-22 10:06:21.285546	2025-04-22 10:06:21.28555	1
823	187	2025-04-05	\N	\N	present	\N	2025-04-22 10:06:21.37653	2025-04-22 10:06:21.376536	1
824	188	2025-04-05	\N	\N	present	\N	2025-04-22 10:06:21.465054	2025-04-22 10:06:21.465059	1
825	184	2025-04-06	\N	\N	present	\N	2025-04-22 10:06:37.202153	2025-04-22 10:06:37.202158	1
826	185	2025-04-06	\N	\N	present	\N	2025-04-22 10:06:37.287954	2025-04-22 10:06:37.287959	1
827	186	2025-04-06	\N	\N	present	\N	2025-04-22 10:06:37.373598	2025-04-22 10:06:37.373603	1
828	187	2025-04-06	\N	\N	present	\N	2025-04-22 10:06:37.459288	2025-04-22 10:06:37.459293	1
829	188	2025-04-06	\N	\N	present	\N	2025-04-22 10:06:37.545117	2025-04-22 10:06:37.545123	1
830	184	2025-04-07	\N	\N	present	\N	2025-04-22 10:06:54.034329	2025-04-22 10:06:54.034334	1
831	185	2025-04-07	\N	\N	present	\N	2025-04-22 10:06:54.120614	2025-04-22 10:06:54.12062	1
832	186	2025-04-07	\N	\N	present	\N	2025-04-22 10:06:54.207224	2025-04-22 10:06:54.207229	1
833	187	2025-04-07	\N	\N	present	\N	2025-04-22 10:06:54.301717	2025-04-22 10:06:54.301722	1
834	188	2025-04-07	\N	\N	present	\N	2025-04-22 10:06:54.387542	2025-04-22 10:06:54.387547	1
835	184	2025-04-08	\N	\N	present	\N	2025-04-22 10:07:11.852667	2025-04-22 10:07:11.852672	1
836	185	2025-04-08	\N	\N	present	\N	2025-04-22 10:07:11.938049	2025-04-22 10:07:11.938054	1
837	186	2025-04-08	\N	\N	present	\N	2025-04-22 10:07:12.02416	2025-04-22 10:07:12.024166	1
838	187	2025-04-08	\N	\N	present	\N	2025-04-22 10:07:12.109934	2025-04-22 10:07:12.10994	1
839	188	2025-04-08	\N	\N	present	\N	2025-04-22 10:07:12.195653	2025-04-22 10:07:12.195658	1
840	184	2025-04-09	\N	\N	present	\N	2025-04-22 10:07:32.106918	2025-04-22 10:07:32.106923	1
841	185	2025-04-09	\N	\N	present	\N	2025-04-22 10:07:32.193399	2025-04-22 10:07:32.193404	1
842	186	2025-04-09	\N	\N	present	\N	2025-04-22 10:07:32.279572	2025-04-22 10:07:32.279577	1
843	187	2025-04-09	\N	\N	present	\N	2025-04-22 10:07:32.368084	2025-04-22 10:07:32.368089	1
844	188	2025-04-09	\N	\N	present	\N	2025-04-22 10:07:32.454479	2025-04-22 10:07:32.454528	1
845	184	2025-04-10	\N	\N	present	\N	2025-04-22 10:08:24.575794	2025-04-22 10:08:24.575798	1
846	185	2025-04-10	\N	\N	present	\N	2025-04-22 10:08:24.667497	2025-04-22 10:08:24.667501	1
847	186	2025-04-10	\N	\N	present	\N	2025-04-22 10:08:24.756518	2025-04-22 10:08:24.756523	1
848	187	2025-04-10	\N	\N	present	\N	2025-04-22 10:08:24.851816	2025-04-22 10:08:24.851821	1
849	188	2025-04-10	\N	\N	present	\N	2025-04-22 10:08:24.941137	2025-04-22 10:08:24.941141	1
850	184	2025-04-11	\N	\N	present	\N	2025-04-22 10:08:56.404889	2025-04-22 10:08:56.404895	1
851	185	2025-04-11	\N	\N	present	\N	2025-04-22 10:08:56.495587	2025-04-22 10:08:56.495591	1
852	186	2025-04-11	\N	\N	present	\N	2025-04-22 10:08:56.585209	2025-04-22 10:08:56.585215	1
853	187	2025-04-11	\N	\N	present	\N	2025-04-22 10:08:56.682412	2025-04-22 10:08:56.682418	1
854	188	2025-04-11	\N	\N	present	\N	2025-04-22 10:08:56.78697	2025-04-22 10:08:56.786975	1
855	184	2025-04-12	\N	\N	present	\N	2025-04-22 10:09:15.223819	2025-04-22 10:09:15.223824	1
856	185	2025-04-12	\N	\N	present	\N	2025-04-22 10:09:15.32312	2025-04-22 10:09:15.323125	1
857	186	2025-04-12	\N	\N	present	\N	2025-04-22 10:09:15.414117	2025-04-22 10:09:15.414121	1
858	187	2025-04-12	\N	\N	present	\N	2025-04-22 10:09:15.504579	2025-04-22 10:09:15.504585	1
859	188	2025-04-12	\N	\N	present	\N	2025-04-22 10:09:15.594843	2025-04-22 10:09:15.594848	1
860	184	2025-04-13	\N	\N	present	\N	2025-04-22 10:09:39.181752	2025-04-22 10:09:39.181757	1
861	185	2025-04-13	\N	\N	present	\N	2025-04-22 10:09:39.275795	2025-04-22 10:09:39.275799	1
862	186	2025-04-13	\N	\N	present	\N	2025-04-22 10:09:39.366191	2025-04-22 10:09:39.366195	1
863	187	2025-04-13	\N	\N	present	\N	2025-04-22 10:09:39.455603	2025-04-22 10:09:39.455608	1
864	188	2025-04-13	\N	\N	present	\N	2025-04-22 10:09:39.581668	2025-04-22 10:09:39.581673	1
865	184	2025-04-14	\N	\N	present	\N	2025-04-22 10:09:56.058983	2025-04-22 10:09:56.058988	1
866	185	2025-04-14	\N	\N	present	\N	2025-04-22 10:09:56.148126	2025-04-22 10:09:56.148131	1
867	186	2025-04-14	\N	\N	present	\N	2025-04-22 10:09:56.237632	2025-04-22 10:09:56.237637	1
868	187	2025-04-14	\N	\N	present	\N	2025-04-22 10:09:56.328153	2025-04-22 10:09:56.328159	1
869	188	2025-04-14	\N	\N	present	\N	2025-04-22 10:09:56.417692	2025-04-22 10:09:56.417697	1
870	184	2025-04-15	\N	\N	present	\N	2025-04-22 10:10:13.968137	2025-04-22 10:10:13.968142	1
871	185	2025-04-15	\N	\N	present	\N	2025-04-22 10:10:14.065304	2025-04-22 10:10:14.065308	1
872	186	2025-04-15	\N	\N	present	\N	2025-04-22 10:10:14.163011	2025-04-22 10:10:14.163016	1
873	187	2025-04-15	\N	\N	present	\N	2025-04-22 10:10:14.259603	2025-04-22 10:10:14.259609	1
874	188	2025-04-15	\N	\N	present	\N	2025-04-22 10:10:14.349938	2025-04-22 10:10:14.349943	1
875	184	2025-04-16	\N	\N	present	\N	2025-04-22 10:11:00.292342	2025-04-22 10:11:00.292348	1
876	185	2025-04-16	\N	\N	present	\N	2025-04-22 10:11:00.382662	2025-04-22 10:11:00.382666	1
877	186	2025-04-16	\N	\N	present	\N	2025-04-22 10:11:00.473349	2025-04-22 10:11:00.473355	1
878	187	2025-04-16	\N	\N	present	\N	2025-04-22 10:11:00.569244	2025-04-22 10:11:00.569249	1
879	188	2025-04-16	\N	\N	present	\N	2025-04-22 10:11:00.659617	2025-04-22 10:11:00.659622	1
880	184	2025-04-17	\N	\N	present	\N	2025-04-22 10:11:54.292089	2025-04-22 10:11:54.292095	1
881	185	2025-04-17	\N	\N	present	\N	2025-04-22 10:11:54.385777	2025-04-22 10:11:54.385781	1
882	186	2025-04-17	\N	\N	present	\N	2025-04-22 10:11:54.476204	2025-04-22 10:11:54.476211	1
883	187	2025-04-17	\N	\N	present	\N	2025-04-22 10:11:54.566783	2025-04-22 10:11:54.566789	1
884	188	2025-04-17	\N	\N	present	\N	2025-04-22 10:11:54.672213	2025-04-22 10:11:54.672218	1
885	184	2025-04-18	\N	\N	present	\N	2025-04-22 10:12:21.729896	2025-04-22 10:12:21.729901	1
886	185	2025-04-18	\N	\N	present	\N	2025-04-22 10:12:21.819823	2025-04-22 10:12:21.819828	1
887	186	2025-04-18	\N	\N	present	\N	2025-04-22 10:12:21.908831	2025-04-22 10:12:21.908836	1
888	187	2025-04-18	\N	\N	present	\N	2025-04-22 10:12:22.007888	2025-04-22 10:12:22.007894	1
798	180	2025-04-22	\N	\N	sick		2025-04-21 23:37:45.74796	2025-04-23 09:09:56.749918	1
892	186	2025-04-19	\N	\N	present	\N	2025-04-22 10:12:55.527629	2025-04-22 10:12:55.527634	1
893	187	2025-04-19	\N	\N	present	\N	2025-04-22 10:12:55.617077	2025-04-22 10:12:55.617082	1
894	188	2025-04-19	\N	\N	present	\N	2025-04-22 10:12:55.708479	2025-04-22 10:12:55.708484	1
895	184	2025-04-20	\N	\N	present	\N	2025-04-22 10:13:23.961737	2025-04-22 10:13:23.961742	1
896	185	2025-04-20	\N	\N	present	\N	2025-04-22 10:13:24.051969	2025-04-22 10:13:24.051975	1
897	186	2025-04-20	\N	\N	present	\N	2025-04-22 10:13:24.142415	2025-04-22 10:13:24.142425	1
898	187	2025-04-20	\N	\N	present	\N	2025-04-22 10:13:24.235417	2025-04-22 10:13:24.235422	1
899	188	2025-04-20	\N	\N	present	\N	2025-04-22 10:13:24.325311	2025-04-22 10:13:24.325316	1
900	184	2025-04-21	\N	\N	present	\N	2025-04-22 10:14:11.813568	2025-04-22 10:14:11.813573	1
901	185	2025-04-21	\N	\N	present	\N	2025-04-22 10:14:11.903855	2025-04-22 10:14:11.90386	1
902	186	2025-04-21	\N	\N	present	\N	2025-04-22 10:14:11.993825	2025-04-22 10:14:11.99383	1
903	187	2025-04-21	\N	\N	present	\N	2025-04-22 10:14:12.083773	2025-04-22 10:14:12.083778	1
904	188	2025-04-21	\N	\N	present	\N	2025-04-22 10:14:12.174619	2025-04-22 10:14:12.174625	1
905	184	2025-04-22	\N	\N	present	\N	2025-04-22 10:14:39.322812	2025-04-22 10:14:39.322817	1
906	185	2025-04-22	\N	\N	present	\N	2025-04-22 10:14:39.414912	2025-04-22 10:14:39.414916	1
907	186	2025-04-22	\N	\N	present	\N	2025-04-22 10:14:39.504449	2025-04-22 10:14:39.504454	1
908	187	2025-04-22	\N	\N	present	\N	2025-04-22 10:14:39.594652	2025-04-22 10:14:39.594656	1
909	188	2025-04-22	\N	\N	present	\N	2025-04-22 10:14:39.687413	2025-04-22 10:14:39.687418	1
912	181	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:07.92569	2025-04-22 20:31:07.925695	1
913	179	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.006314	2025-04-22 20:31:08.006319	1
914	178	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.087657	2025-04-22 20:31:08.087662	1
915	183	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.169215	2025-04-22 20:31:08.169218	1
916	182	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.250193	2025-04-22 20:31:08.250198	1
917	175	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.333068	2025-04-22 20:31:08.333072	1
918	173	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.413658	2025-04-22 20:31:08.413662	1
919	172	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.494911	2025-04-22 20:31:08.494915	1
921	171	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.656993	2025-04-22 20:31:08.656998	1
922	174	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.737601	2025-04-22 20:31:08.737606	1
923	177	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.818214	2025-04-22 20:31:08.818218	1
924	169	2025-04-23	\N	\N	present	\N	2025-04-22 20:31:08.898786	2025-04-22 20:31:08.89879	1
927	184	2025-04-23	\N	\N	present	\N	2025-04-22 20:32:04.852403	2025-04-22 20:32:04.852408	1
928	185	2025-04-23	\N	\N	present	\N	2025-04-22 20:32:04.941574	2025-04-22 20:32:04.941579	1
929	186	2025-04-23	\N	\N	present	\N	2025-04-22 20:32:05.057267	2025-04-22 20:32:05.057271	1
930	187	2025-04-23	\N	\N	present	\N	2025-04-22 20:32:05.146557	2025-04-22 20:32:05.146562	1
931	188	2025-04-23	\N	\N	present	\N	2025-04-22 20:32:05.247087	2025-04-22 20:32:05.247108	1
543	180	2025-04-21	\N	\N	sick		2025-04-21 23:10:53.124362	2025-04-23 09:08:49.272178	1
932	189	2025-04-01	\N	\N	present	\N	2025-04-23 10:20:45.123774	2025-04-23 10:20:45.123779	1
933	190	2025-04-01	\N	\N	present	\N	2025-04-23 10:20:45.215893	2025-04-23 10:20:45.215903	1
934	191	2025-04-01	\N	\N	present	\N	2025-04-23 10:20:45.304358	2025-04-23 10:20:45.304362	1
935	192	2025-04-01	\N	\N	present	\N	2025-04-23 10:20:45.392744	2025-04-23 10:20:45.392748	1
936	193	2025-04-01	\N	\N	present	\N	2025-04-23 10:20:45.478367	2025-04-23 10:20:45.478379	1
937	189	2025-04-02	\N	\N	present	\N	2025-04-23 10:21:09.655452	2025-04-23 10:21:09.655458	1
938	190	2025-04-02	\N	\N	present	\N	2025-04-23 10:21:09.741328	2025-04-23 10:21:09.741332	1
939	191	2025-04-02	\N	\N	present	\N	2025-04-23 10:21:09.827035	2025-04-23 10:21:09.827039	1
940	192	2025-04-02	\N	\N	present	\N	2025-04-23 10:21:09.918107	2025-04-23 10:21:09.918112	1
941	193	2025-04-02	\N	\N	present	\N	2025-04-23 10:21:10.003528	2025-04-23 10:21:10.003532	1
942	189	2025-04-03	\N	\N	present	\N	2025-04-23 10:21:26.851078	2025-04-23 10:21:26.851082	1
943	190	2025-04-03	\N	\N	present	\N	2025-04-23 10:21:26.93876	2025-04-23 10:21:26.938764	1
944	191	2025-04-03	\N	\N	present	\N	2025-04-23 10:21:27.027395	2025-04-23 10:21:27.027399	1
945	192	2025-04-03	\N	\N	present	\N	2025-04-23 10:21:27.115139	2025-04-23 10:21:27.115143	1
946	193	2025-04-03	\N	\N	present	\N	2025-04-23 10:21:27.203013	2025-04-23 10:21:27.203018	1
947	189	2025-04-04	\N	\N	present	\N	2025-04-23 10:21:49.162357	2025-04-23 10:21:49.162362	1
948	190	2025-04-04	\N	\N	present	\N	2025-04-23 10:21:49.250009	2025-04-23 10:21:49.250013	1
949	191	2025-04-04	\N	\N	present	\N	2025-04-23 10:21:49.337747	2025-04-23 10:21:49.337752	1
950	192	2025-04-04	\N	\N	present	\N	2025-04-23 10:21:49.425447	2025-04-23 10:21:49.425453	1
951	193	2025-04-04	\N	\N	present	\N	2025-04-23 10:21:49.51351	2025-04-23 10:21:49.513515	1
952	189	2025-04-05	\N	\N	present	\N	2025-04-23 10:22:11.99724	2025-04-23 10:22:11.997245	1
953	190	2025-04-05	\N	\N	present	\N	2025-04-23 10:22:12.084968	2025-04-23 10:22:12.084973	1
954	191	2025-04-05	\N	\N	present	\N	2025-04-23 10:22:12.172856	2025-04-23 10:22:12.172861	1
955	192	2025-04-05	\N	\N	present	\N	2025-04-23 10:22:12.261158	2025-04-23 10:22:12.261163	1
956	193	2025-04-05	\N	\N	present	\N	2025-04-23 10:22:12.349325	2025-04-23 10:22:12.34933	1
957	189	2025-04-06	\N	\N	present	\N	2025-04-23 10:22:39.827866	2025-04-23 10:22:39.827871	1
958	190	2025-04-06	\N	\N	present	\N	2025-04-23 10:22:39.915052	2025-04-23 10:22:39.915057	1
959	191	2025-04-06	\N	\N	present	\N	2025-04-23 10:22:40.001477	2025-04-23 10:22:40.001483	1
960	192	2025-04-06	\N	\N	present	\N	2025-04-23 10:22:40.088868	2025-04-23 10:22:40.088873	1
961	193	2025-04-06	\N	\N	present	\N	2025-04-23 10:22:40.175245	2025-04-23 10:22:40.17525	1
962	189	2025-04-07	\N	\N	present	\N	2025-04-23 10:22:57.13259	2025-04-23 10:22:57.132595	1
963	190	2025-04-07	\N	\N	present	\N	2025-04-23 10:22:57.217932	2025-04-23 10:22:57.217937	1
964	191	2025-04-07	\N	\N	present	\N	2025-04-23 10:22:57.304786	2025-04-23 10:22:57.30479	1
965	192	2025-04-07	\N	\N	present	\N	2025-04-23 10:22:57.390563	2025-04-23 10:22:57.390568	1
966	193	2025-04-07	\N	\N	present	\N	2025-04-23 10:22:57.47742	2025-04-23 10:22:57.477424	1
967	189	2025-04-08	\N	\N	present	\N	2025-04-23 10:23:14.415241	2025-04-23 10:23:14.415245	1
968	190	2025-04-08	\N	\N	present	\N	2025-04-23 10:23:14.501098	2025-04-23 10:23:14.501103	1
969	191	2025-04-08	\N	\N	present	\N	2025-04-23 10:23:14.588837	2025-04-23 10:23:14.588841	1
970	192	2025-04-08	\N	\N	present	\N	2025-04-23 10:23:14.677226	2025-04-23 10:23:14.677231	1
971	193	2025-04-08	\N	\N	present	\N	2025-04-23 10:23:14.763156	2025-04-23 10:23:14.76316	1
972	189	2025-04-09	\N	\N	present	\N	2025-04-23 10:23:54.925592	2025-04-23 10:23:54.925596	1
973	190	2025-04-09	\N	\N	present	\N	2025-04-23 10:23:55.015915	2025-04-23 10:23:55.01592	1
974	191	2025-04-09	\N	\N	present	\N	2025-04-23 10:23:55.104537	2025-04-23 10:23:55.104542	1
975	192	2025-04-09	\N	\N	present	\N	2025-04-23 10:23:55.192932	2025-04-23 10:23:55.192938	1
976	193	2025-04-09	\N	\N	present	\N	2025-04-23 10:23:55.280922	2025-04-23 10:23:55.280927	1
977	189	2025-04-10	\N	\N	present	\N	2025-04-23 10:24:10.469386	2025-04-23 10:24:10.469391	1
978	190	2025-04-10	\N	\N	present	\N	2025-04-23 10:24:10.557878	2025-04-23 10:24:10.557883	1
979	191	2025-04-10	\N	\N	present	\N	2025-04-23 10:24:10.647198	2025-04-23 10:24:10.647203	1
980	192	2025-04-10	\N	\N	present	\N	2025-04-23 10:24:10.735587	2025-04-23 10:24:10.735592	1
981	193	2025-04-10	\N	\N	present	\N	2025-04-23 10:24:10.826855	2025-04-23 10:24:10.82686	1
982	189	2025-04-11	\N	\N	present	\N	2025-04-23 10:24:27.940352	2025-04-23 10:24:27.940356	1
983	190	2025-04-11	\N	\N	present	\N	2025-04-23 10:24:28.030276	2025-04-23 10:24:28.030281	1
984	191	2025-04-11	\N	\N	present	\N	2025-04-23 10:24:28.119533	2025-04-23 10:24:28.119538	1
985	192	2025-04-11	\N	\N	present	\N	2025-04-23 10:24:28.208292	2025-04-23 10:24:28.208297	1
986	193	2025-04-11	\N	\N	present	\N	2025-04-23 10:24:28.296908	2025-04-23 10:24:28.296913	1
987	189	2025-04-12	\N	\N	present	\N	2025-04-23 10:24:52.021712	2025-04-23 10:24:52.021717	1
988	190	2025-04-12	\N	\N	present	\N	2025-04-23 10:24:52.110441	2025-04-23 10:24:52.110445	1
989	191	2025-04-12	\N	\N	present	\N	2025-04-23 10:24:52.198778	2025-04-23 10:24:52.198782	1
990	192	2025-04-12	\N	\N	present	\N	2025-04-23 10:24:52.287773	2025-04-23 10:24:52.287777	1
991	193	2025-04-12	\N	\N	present	\N	2025-04-23 10:24:52.376205	2025-04-23 10:24:52.37621	1
992	189	2025-04-13	\N	\N	present	\N	2025-04-23 10:25:28.924573	2025-04-23 10:25:28.924578	1
993	190	2025-04-13	\N	\N	present	\N	2025-04-23 10:25:29.013233	2025-04-23 10:25:29.013237	1
994	191	2025-04-13	\N	\N	present	\N	2025-04-23 10:25:29.101609	2025-04-23 10:25:29.101614	1
911	180	2025-04-23	\N	\N	sick		2025-04-22 20:31:07.842525	2025-04-30 12:05:18.917203	1
1003	190	2025-04-23	\N	\N	present	\N	2025-04-23 10:26:03.714379	2025-04-23 10:26:03.714384	1
1004	191	2025-04-23	\N	\N	present	\N	2025-04-23 10:26:03.802411	2025-04-23 10:26:03.802416	1
1005	192	2025-04-23	\N	\N	present	\N	2025-04-23 10:26:03.89245	2025-04-23 10:26:03.892455	1
1006	193	2025-04-23	\N	\N	present	\N	2025-04-23 10:26:03.984103	2025-04-23 10:26:03.984108	1
1007	189	2025-04-15	\N	\N	present	\N	2025-04-23 10:26:20.610358	2025-04-23 10:26:20.610363	1
1008	190	2025-04-15	\N	\N	present	\N	2025-04-23 10:26:20.719189	2025-04-23 10:26:20.719193	1
1009	191	2025-04-15	\N	\N	present	\N	2025-04-23 10:26:20.808633	2025-04-23 10:26:20.808637	1
1010	192	2025-04-15	\N	\N	present	\N	2025-04-23 10:26:20.91692	2025-04-23 10:26:20.916925	1
1011	193	2025-04-15	\N	\N	present	\N	2025-04-23 10:26:21.011359	2025-04-23 10:26:21.011364	1
1012	189	2025-04-16	\N	\N	present	\N	2025-04-23 10:26:36.033982	2025-04-23 10:26:36.033987	1
1013	190	2025-04-16	\N	\N	present	\N	2025-04-23 10:26:36.12246	2025-04-23 10:26:36.122465	1
1014	191	2025-04-16	\N	\N	present	\N	2025-04-23 10:26:36.210651	2025-04-23 10:26:36.210657	1
1015	192	2025-04-16	\N	\N	present	\N	2025-04-23 10:26:36.299158	2025-04-23 10:26:36.299163	1
1016	193	2025-04-16	\N	\N	present	\N	2025-04-23 10:26:36.388177	2025-04-23 10:26:36.388182	1
1017	189	2025-04-18	\N	\N	present	\N	2025-04-23 10:26:52.739619	2025-04-23 10:26:52.739624	1
1018	190	2025-04-18	\N	\N	present	\N	2025-04-23 10:26:52.829505	2025-04-23 10:26:52.82951	1
1019	191	2025-04-18	\N	\N	present	\N	2025-04-23 10:26:52.917914	2025-04-23 10:26:52.917919	1
1020	192	2025-04-18	\N	\N	present	\N	2025-04-23 10:26:53.00658	2025-04-23 10:26:53.006586	1
1021	193	2025-04-18	\N	\N	present	\N	2025-04-23 10:26:53.095502	2025-04-23 10:26:53.095507	1
1022	189	2025-04-19	\N	\N	present	\N	2025-04-23 10:27:56.023857	2025-04-23 10:27:56.023862	1
1023	190	2025-04-19	\N	\N	present	\N	2025-04-23 10:27:56.113597	2025-04-23 10:27:56.113601	1
1024	191	2025-04-19	\N	\N	present	\N	2025-04-23 10:27:56.202935	2025-04-23 10:27:56.20294	1
1025	192	2025-04-19	\N	\N	present	\N	2025-04-23 10:27:56.291464	2025-04-23 10:27:56.291469	1
1026	193	2025-04-19	\N	\N	present	\N	2025-04-23 10:27:56.38034	2025-04-23 10:27:56.380345	1
1027	189	2025-04-20	\N	\N	present	\N	2025-04-23 10:28:17.944548	2025-04-23 10:28:17.944553	1
1028	190	2025-04-20	\N	\N	present	\N	2025-04-23 10:28:18.03689	2025-04-23 10:28:18.036895	1
1029	191	2025-04-20	\N	\N	present	\N	2025-04-23 10:28:18.126392	2025-04-23 10:28:18.126397	1
1030	192	2025-04-20	\N	\N	present	\N	2025-04-23 10:28:18.215877	2025-04-23 10:28:18.215882	1
1031	193	2025-04-20	\N	\N	present	\N	2025-04-23 10:28:18.305615	2025-04-23 10:28:18.30562	1
1032	189	2025-04-21	\N	\N	present	\N	2025-04-23 10:28:34.150456	2025-04-23 10:28:34.15046	1
1033	190	2025-04-21	\N	\N	present	\N	2025-04-23 10:28:34.239053	2025-04-23 10:28:34.239058	1
1034	191	2025-04-21	\N	\N	present	\N	2025-04-23 10:28:34.327511	2025-04-23 10:28:34.327516	1
1035	192	2025-04-21	\N	\N	present	\N	2025-04-23 10:28:34.41642	2025-04-23 10:28:34.416425	1
1036	193	2025-04-21	\N	\N	present	\N	2025-04-23 10:28:34.505467	2025-04-23 10:28:34.505472	1
1037	189	2025-04-17	\N	\N	present	\N	2025-04-23 10:30:22.831396	2025-04-23 10:30:22.831401	1
1038	190	2025-04-17	\N	\N	present	\N	2025-04-23 10:30:22.918704	2025-04-23 10:30:22.918709	1
1039	191	2025-04-17	\N	\N	present	\N	2025-04-23 10:30:23.005661	2025-04-23 10:30:23.005666	1
1040	192	2025-04-17	\N	\N	present	\N	2025-04-23 10:30:23.095028	2025-04-23 10:30:23.095033	1
1041	193	2025-04-17	\N	\N	present	\N	2025-04-23 10:30:23.186032	2025-04-23 10:30:23.186037	1
1042	189	2025-04-22	\N	\N	present	\N	2025-04-23 10:30:43.383865	2025-04-23 10:30:43.38387	1
1043	190	2025-04-22	\N	\N	present	\N	2025-04-23 10:30:43.471096	2025-04-23 10:30:43.471102	1
1044	191	2025-04-22	\N	\N	present	\N	2025-04-23 10:30:43.56052	2025-04-23 10:30:43.560525	1
1045	192	2025-04-22	\N	\N	present	\N	2025-04-23 10:30:43.648144	2025-04-23 10:30:43.648149	1
1046	193	2025-04-22	\N	\N	present	\N	2025-04-23 10:30:43.73498	2025-04-23 10:30:43.734984	1
2521	214	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:57.169972	2025-04-23 13:35:57.169976	1
2523	194	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:57.343352	2025-04-23 13:35:57.343356	1
2524	195	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:57.434517	2025-04-23 13:35:57.434521	1
2525	196	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:57.52134	2025-04-23 13:35:57.521344	1
2526	197	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:57.608498	2025-04-23 13:35:57.608502	1
2527	198	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:57.697488	2025-04-23 13:35:57.697493	1
2529	200	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:57.87545	2025-04-23 13:35:57.875454	1
2530	201	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:57.967036	2025-04-23 13:35:57.96704	1
2531	202	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.056838	2025-04-23 13:35:58.056842	1
2532	203	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.143976	2025-04-23 13:35:58.14398	1
2533	204	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.230441	2025-04-23 13:35:58.230445	1
2534	205	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.317322	2025-04-23 13:35:58.317326	1
2535	206	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.404078	2025-04-23 13:35:58.404082	1
2536	207	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.494462	2025-04-23 13:35:58.494465	1
2537	208	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.587009	2025-04-23 13:35:58.587019	1
2538	209	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.67456	2025-04-23 13:35:58.674563	1
2539	210	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.763254	2025-04-23 13:35:58.763258	1
2540	211	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.850517	2025-04-23 13:35:58.850521	1
2541	212	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:58.937992	2025-04-23 13:35:58.937996	1
2543	214	2025-04-06	\N	\N	present	\N	2025-04-23 13:35:59.112122	2025-04-23 13:35:59.112126	1
2545	194	2025-04-07	\N	\N	present	\N	2025-04-23 13:35:59.287214	2025-04-23 13:35:59.287217	1
2546	195	2025-04-07	\N	\N	present	\N	2025-04-23 13:35:59.38023	2025-04-23 13:35:59.380234	1
2547	196	2025-04-07	\N	\N	present	\N	2025-04-23 13:35:59.46831	2025-04-23 13:35:59.468313	1
2548	197	2025-04-07	\N	\N	present	\N	2025-04-23 13:35:59.555238	2025-04-23 13:35:59.555241	1
2549	198	2025-04-07	\N	\N	present	\N	2025-04-23 13:35:59.643061	2025-04-23 13:35:59.643065	1
2551	200	2025-04-07	\N	\N	present	\N	2025-04-23 13:35:59.824209	2025-04-23 13:35:59.824214	1
2552	201	2025-04-07	\N	\N	present	\N	2025-04-23 13:35:59.911411	2025-04-23 13:35:59.911415	1
2553	202	2025-04-07	\N	\N	present	\N	2025-04-23 13:35:59.999569	2025-04-23 13:35:59.999572	1
2554	203	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:00.08707	2025-04-23 13:36:00.087073	1
2555	204	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:00.17443	2025-04-23 13:36:00.174433	1
2556	205	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:00.269783	2025-04-23 13:36:00.269786	1
2557	206	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:00.359772	2025-04-23 13:36:00.359776	1
2558	207	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:00.450689	2025-04-23 13:36:00.450694	1
2559	208	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:00.561498	2025-04-23 13:36:00.561502	1
2560	209	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:00.652065	2025-04-23 13:36:00.652068	1
2561	210	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:00.739861	2025-04-23 13:36:00.739864	1
2562	211	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:00.827216	2025-04-23 13:36:00.82722	1
2563	212	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:00.918921	2025-04-23 13:36:00.918926	1
2565	214	2025-04-07	\N	\N	present	\N	2025-04-23 13:36:01.093103	2025-04-23 13:36:01.093105	1
2567	194	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:01.268435	2025-04-23 13:36:01.268439	1
2568	195	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:01.358628	2025-04-23 13:36:01.358631	1
2569	196	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:01.445991	2025-04-23 13:36:01.445994	1
2570	197	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:01.535258	2025-04-23 13:36:01.535262	1
2571	198	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:01.621868	2025-04-23 13:36:01.621871	1
2573	200	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:01.797032	2025-04-23 13:36:01.797035	1
2574	201	2025-04-08	\N	\N	present	\N	2025-04-23 13:36:01.885354	2025-04-23 13:36:01.885358	1
2589	194	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:03.198276	2025-04-23 13:36:03.19828	1
2590	195	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:03.285339	2025-04-23 13:36:03.285344	1
2591	196	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:03.37239	2025-04-23 13:36:03.372394	1
2592	197	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:03.458855	2025-04-23 13:36:03.458859	1
2593	198	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:03.545984	2025-04-23 13:36:03.545987	1
2595	200	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:03.720707	2025-04-23 13:36:03.720711	1
2596	201	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:03.807306	2025-04-23 13:36:03.807311	1
2597	202	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:03.894054	2025-04-23 13:36:03.894057	1
2598	203	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:03.981642	2025-04-23 13:36:03.981646	1
2599	204	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:04.06865	2025-04-23 13:36:04.068653	1
2600	205	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:04.156104	2025-04-23 13:36:04.156109	1
2601	206	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:04.243255	2025-04-23 13:36:04.243259	1
2602	207	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:04.330414	2025-04-23 13:36:04.330418	1
2603	208	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:04.417618	2025-04-23 13:36:04.417622	1
2604	209	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:04.504615	2025-04-23 13:36:04.50462	1
2605	210	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:04.592008	2025-04-23 13:36:04.592011	1
2606	211	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:04.679031	2025-04-23 13:36:04.679034	1
2607	212	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:04.76535	2025-04-23 13:36:04.765353	1
2609	214	2025-04-09	\N	\N	present	\N	2025-04-23 13:36:04.939217	2025-04-23 13:36:04.939221	1
2611	194	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:05.112723	2025-04-23 13:36:05.112726	1
2612	195	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:05.278117	2025-04-23 13:36:05.278121	1
2613	196	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:05.365114	2025-04-23 13:36:05.365117	1
2614	197	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:05.451672	2025-04-23 13:36:05.451675	1
2615	198	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:05.538608	2025-04-23 13:36:05.538612	1
2617	200	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:05.71388	2025-04-23 13:36:05.713883	1
2618	201	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:05.801072	2025-04-23 13:36:05.801077	1
2619	202	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:05.888464	2025-04-23 13:36:05.888467	1
2620	203	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:05.975165	2025-04-23 13:36:05.975169	1
2621	204	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:06.062678	2025-04-23 13:36:06.062681	1
2622	205	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:06.150096	2025-04-23 13:36:06.150101	1
2623	206	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:06.237598	2025-04-23 13:36:06.237602	1
2624	207	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:06.324712	2025-04-23 13:36:06.324716	1
2625	208	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:06.411547	2025-04-23 13:36:06.411551	1
2626	209	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:06.498355	2025-04-23 13:36:06.498359	1
2627	210	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:06.586927	2025-04-23 13:36:06.586931	1
2628	211	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:06.673744	2025-04-23 13:36:06.673747	1
2629	212	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:06.760488	2025-04-23 13:36:06.760492	1
2631	214	2025-04-10	\N	\N	present	\N	2025-04-23 13:36:06.934314	2025-04-23 13:36:06.934318	1
2633	194	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:40.834281	2025-04-23 13:36:40.834286	1
2634	195	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:40.921568	2025-04-23 13:36:40.921572	1
2635	196	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.008588	2025-04-23 13:36:41.008592	1
2636	197	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.096108	2025-04-23 13:36:41.096112	1
2637	198	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.182849	2025-04-23 13:36:41.182853	1
2639	200	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.357042	2025-04-23 13:36:41.357046	1
2640	201	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.445652	2025-04-23 13:36:41.445656	1
2641	202	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.532745	2025-04-23 13:36:41.532749	1
2642	203	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.619789	2025-04-23 13:36:41.619793	1
2643	204	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.708986	2025-04-23 13:36:41.70899	1
2644	205	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.797796	2025-04-23 13:36:41.797799	1
2645	206	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.884592	2025-04-23 13:36:41.884596	1
2646	207	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:41.971883	2025-04-23 13:36:41.971887	1
2647	208	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:42.058889	2025-04-23 13:36:42.058911	1
2648	209	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:42.146071	2025-04-23 13:36:42.146075	1
2649	210	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:42.238052	2025-04-23 13:36:42.238055	1
2650	211	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:42.325295	2025-04-23 13:36:42.325299	1
2651	212	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:42.412307	2025-04-23 13:36:42.412312	1
2653	214	2025-04-11	\N	\N	present	\N	2025-04-23 13:36:42.59093	2025-04-23 13:36:42.590934	1
2655	194	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:42.769562	2025-04-23 13:36:42.769566	1
2656	195	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:42.856475	2025-04-23 13:36:42.856479	1
2657	196	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:42.945023	2025-04-23 13:36:42.945028	1
2658	197	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.032588	2025-04-23 13:36:43.032592	1
2659	198	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.120584	2025-04-23 13:36:43.120588	1
2661	200	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.295185	2025-04-23 13:36:43.295189	1
2662	201	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.382063	2025-04-23 13:36:43.382067	1
2663	202	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.468832	2025-04-23 13:36:43.468836	1
2664	203	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.555971	2025-04-23 13:36:43.555975	1
2665	204	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.643052	2025-04-23 13:36:43.643057	1
2666	205	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.735826	2025-04-23 13:36:43.73583	1
2667	206	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.822883	2025-04-23 13:36:43.822887	1
2668	207	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.910601	2025-04-23 13:36:43.910605	1
2669	208	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:43.997682	2025-04-23 13:36:43.997686	1
2670	209	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:44.088473	2025-04-23 13:36:44.088478	1
2671	210	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:44.175869	2025-04-23 13:36:44.175873	1
2672	211	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:44.262788	2025-04-23 13:36:44.262792	1
2673	212	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:44.350164	2025-04-23 13:36:44.350168	1
2675	214	2025-04-12	\N	\N	present	\N	2025-04-23 13:36:44.523824	2025-04-23 13:36:44.523827	1
2677	194	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:44.700124	2025-04-23 13:36:44.700128	1
2678	195	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:44.790442	2025-04-23 13:36:44.790446	1
2679	196	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:44.87723	2025-04-23 13:36:44.877234	1
2680	197	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:44.964713	2025-04-23 13:36:44.964717	1
2681	198	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:45.05137	2025-04-23 13:36:45.051374	1
2697	214	2025-04-13	\N	\N	present	\N	2025-04-23 13:36:46.443658	2025-04-23 13:36:46.443673	1
2699	194	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:46.619789	2025-04-23 13:36:46.619792	1
2700	195	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:46.706172	2025-04-23 13:36:46.706176	1
2701	196	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:46.792798	2025-04-23 13:36:46.792801	1
2702	197	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:46.879626	2025-04-23 13:36:46.879631	1
2703	198	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:46.966113	2025-04-23 13:36:46.966116	1
2705	200	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:47.140149	2025-04-23 13:36:47.140153	1
2706	201	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:47.227685	2025-04-23 13:36:47.227688	1
2707	202	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:47.314686	2025-04-23 13:36:47.314691	1
2708	203	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:47.401885	2025-04-23 13:36:47.401888	1
2709	204	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:47.488792	2025-04-23 13:36:47.488796	1
2710	205	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:47.576503	2025-04-23 13:36:47.576508	1
2711	206	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:47.66329	2025-04-23 13:36:47.663294	1
2712	207	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:47.74987	2025-04-23 13:36:47.749874	1
2713	208	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:47.836529	2025-04-23 13:36:47.836533	1
2714	209	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:47.924341	2025-04-23 13:36:47.924344	1
2715	210	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:48.012498	2025-04-23 13:36:48.012501	1
2716	211	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:48.099401	2025-04-23 13:36:48.099405	1
2717	212	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:48.187184	2025-04-23 13:36:48.187187	1
2719	214	2025-04-14	\N	\N	present	\N	2025-04-23 13:36:48.364508	2025-04-23 13:36:48.364511	1
2721	194	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:48.540958	2025-04-23 13:36:48.540961	1
2722	195	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:48.628162	2025-04-23 13:36:48.628167	1
2723	196	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:48.718611	2025-04-23 13:36:48.718614	1
2724	197	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:48.809331	2025-04-23 13:36:48.809335	1
2725	198	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:48.896643	2025-04-23 13:36:48.896647	1
2727	200	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.080357	2025-04-23 13:36:49.080361	1
2728	201	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.168876	2025-04-23 13:36:49.168879	1
2729	202	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.257102	2025-04-23 13:36:49.257107	1
2730	203	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.353291	2025-04-23 13:36:49.353295	1
2731	204	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.449474	2025-04-23 13:36:49.449477	1
2732	205	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.536349	2025-04-23 13:36:49.536353	1
2733	206	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.624215	2025-04-23 13:36:49.624218	1
2734	207	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.727843	2025-04-23 13:36:49.727847	1
2735	208	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.82065	2025-04-23 13:36:49.820655	1
2736	209	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.909203	2025-04-23 13:36:49.909206	1
2737	210	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:49.997133	2025-04-23 13:36:49.997136	1
2738	211	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:50.085815	2025-04-23 13:36:50.085819	1
2739	212	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:50.172651	2025-04-23 13:36:50.172654	1
2741	214	2025-04-15	\N	\N	present	\N	2025-04-23 13:36:50.347436	2025-04-23 13:36:50.347439	1
2743	194	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:50.521462	2025-04-23 13:36:50.521466	1
2744	195	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:50.6097	2025-04-23 13:36:50.609703	1
2745	196	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:50.696074	2025-04-23 13:36:50.696077	1
2746	197	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:50.782486	2025-04-23 13:36:50.78249	1
2747	198	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:50.869596	2025-04-23 13:36:50.869599	1
2749	200	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.042947	2025-04-23 13:36:51.04295	1
2750	201	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.129213	2025-04-23 13:36:51.129216	1
2751	202	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.215569	2025-04-23 13:36:51.215572	1
2752	203	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.302592	2025-04-23 13:36:51.302595	1
2753	204	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.389175	2025-04-23 13:36:51.389179	1
2754	205	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.475871	2025-04-23 13:36:51.475874	1
2755	206	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.56275	2025-04-23 13:36:51.562753	1
2756	207	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.649345	2025-04-23 13:36:51.649349	1
2757	208	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.73649	2025-04-23 13:36:51.736493	1
2758	209	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.823094	2025-04-23 13:36:51.823097	1
2759	210	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.909714	2025-04-23 13:36:51.909717	1
2760	211	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:51.996229	2025-04-23 13:36:51.996232	1
2761	212	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:52.083063	2025-04-23 13:36:52.083067	1
2763	214	2025-04-16	\N	\N	present	\N	2025-04-23 13:36:52.256769	2025-04-23 13:36:52.256773	1
2765	194	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:52.431717	2025-04-23 13:36:52.43172	1
2766	195	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:52.518156	2025-04-23 13:36:52.51816	1
2767	196	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:52.6046	2025-04-23 13:36:52.604604	1
2768	197	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:52.691535	2025-04-23 13:36:52.691538	1
2769	198	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:52.777842	2025-04-23 13:36:52.777846	1
2771	200	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:52.951228	2025-04-23 13:36:52.951232	1
2879	198	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:02.406874	2025-04-23 13:37:02.406879	1
2881	200	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:02.583016	2025-04-23 13:37:02.58302	1
2882	201	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:02.669839	2025-04-23 13:37:02.669843	1
2883	202	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:02.756839	2025-04-23 13:37:02.756843	1
2884	203	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:02.847367	2025-04-23 13:37:02.847371	1
2885	204	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:02.937836	2025-04-23 13:37:02.937841	1
2886	205	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:03.027123	2025-04-23 13:37:03.027127	1
2887	206	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:03.114619	2025-04-23 13:37:03.114622	1
2888	207	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:03.201003	2025-04-23 13:37:03.201006	1
2889	208	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:03.288483	2025-04-23 13:37:03.288487	1
2890	209	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:03.375186	2025-04-23 13:37:03.375191	1
2891	210	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:03.463523	2025-04-23 13:37:03.463527	1
2892	211	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:03.550204	2025-04-23 13:37:03.550208	1
2893	212	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:03.63687	2025-04-23 13:37:03.636875	1
2895	214	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:03.811035	2025-04-23 13:37:03.81104	1
2425	206	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.807498	2025-04-23 13:35:48.807502	1
2426	207	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.894017	2025-04-23 13:35:48.894022	1
2427	208	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:48.985235	2025-04-23 13:35:48.98524	1
2428	209	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:49.07179	2025-04-23 13:35:49.071794	1
2429	210	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:49.158614	2025-04-23 13:35:49.158617	1
2430	211	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:49.248036	2025-04-23 13:35:49.248041	1
2431	212	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:49.334572	2025-04-23 13:35:49.334576	1
2433	214	2025-04-01	\N	\N	present	\N	2025-04-23 13:35:49.509098	2025-04-23 13:35:49.509101	1
2435	194	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:49.683557	2025-04-23 13:35:49.68356	1
2436	195	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:49.770715	2025-04-23 13:35:49.770719	1
2437	196	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:49.857359	2025-04-23 13:35:49.857364	1
2438	197	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:49.944216	2025-04-23 13:35:49.94422	1
2439	198	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.031222	2025-04-23 13:35:50.031226	1
2441	200	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.205377	2025-04-23 13:35:50.205382	1
2442	201	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.292555	2025-04-23 13:35:50.292558	1
2443	202	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.379181	2025-04-23 13:35:50.379185	1
2444	203	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.467349	2025-04-23 13:35:50.467352	1
2445	204	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.55527	2025-04-23 13:35:50.555274	1
2446	205	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.64609	2025-04-23 13:35:50.646094	1
2447	206	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.733355	2025-04-23 13:35:50.733359	1
2448	207	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.820051	2025-04-23 13:35:50.820055	1
2449	208	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.906774	2025-04-23 13:35:50.906778	1
2450	209	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:50.993739	2025-04-23 13:35:50.993742	1
2451	210	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:51.080528	2025-04-23 13:35:51.080531	1
2452	211	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:51.167432	2025-04-23 13:35:51.167436	1
2453	212	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:51.254383	2025-04-23 13:35:51.254387	1
2455	214	2025-04-02	\N	\N	present	\N	2025-04-23 13:35:51.428547	2025-04-23 13:35:51.428551	1
2457	194	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:51.602581	2025-04-23 13:35:51.602584	1
2458	195	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:51.68906	2025-04-23 13:35:51.689065	1
2459	196	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:51.775431	2025-04-23 13:35:51.775444	1
2460	197	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:51.862096	2025-04-23 13:35:51.8621	1
2461	198	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:51.949051	2025-04-23 13:35:51.949054	1
2463	200	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.122224	2025-04-23 13:35:52.122228	1
2464	201	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.208736	2025-04-23 13:35:52.20874	1
2465	202	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.296154	2025-04-23 13:35:52.296159	1
2466	203	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.383274	2025-04-23 13:35:52.383278	1
2467	204	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.469861	2025-04-23 13:35:52.469865	1
2468	205	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.556844	2025-04-23 13:35:52.556848	1
2469	206	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.643657	2025-04-23 13:35:52.643661	1
2470	207	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.730328	2025-04-23 13:35:52.730333	1
2471	208	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.818048	2025-04-23 13:35:52.818052	1
2472	209	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.904716	2025-04-23 13:35:52.90472	1
2473	210	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:52.991193	2025-04-23 13:35:52.991196	1
2474	211	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:53.077818	2025-04-23 13:35:53.077822	1
2475	212	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:53.164768	2025-04-23 13:35:53.164772	1
2477	214	2025-04-03	\N	\N	present	\N	2025-04-23 13:35:53.339377	2025-04-23 13:35:53.33938	1
2479	194	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:53.513404	2025-04-23 13:35:53.513409	1
2480	195	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:53.600467	2025-04-23 13:35:53.600471	1
2481	196	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:53.687123	2025-04-23 13:35:53.687126	1
2482	197	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:53.773937	2025-04-23 13:35:53.773941	1
2483	198	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:53.860485	2025-04-23 13:35:53.860489	1
2485	200	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.033722	2025-04-23 13:35:54.033726	1
2486	201	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.120302	2025-04-23 13:35:54.120305	1
2487	202	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.20673	2025-04-23 13:35:54.206733	1
2488	203	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.293558	2025-04-23 13:35:54.293562	1
2489	204	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.382186	2025-04-23 13:35:54.382189	1
2490	205	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.469175	2025-04-23 13:35:54.469178	1
2491	206	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.555764	2025-04-23 13:35:54.555767	1
2492	207	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.642024	2025-04-23 13:35:54.642028	1
2493	208	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.728952	2025-04-23 13:35:54.728957	1
2494	209	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.815822	2025-04-23 13:35:54.815826	1
2495	210	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.906496	2025-04-23 13:35:54.906499	1
2496	211	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:54.993033	2025-04-23 13:35:54.993037	1
2497	212	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:55.079765	2025-04-23 13:35:55.079768	1
2499	214	2025-04-04	\N	\N	present	\N	2025-04-23 13:35:55.254813	2025-04-23 13:35:55.254817	1
2501	194	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:55.42844	2025-04-23 13:35:55.428443	1
2502	195	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:55.515764	2025-04-23 13:35:55.515769	1
2503	196	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:55.602614	2025-04-23 13:35:55.602618	1
2504	197	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:55.689522	2025-04-23 13:35:55.689526	1
2505	198	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:55.776395	2025-04-23 13:35:55.776399	1
2507	200	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:55.949728	2025-04-23 13:35:55.949731	1
2508	201	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.036548	2025-04-23 13:35:56.036552	1
2509	202	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.123163	2025-04-23 13:35:56.123166	1
2510	203	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.209871	2025-04-23 13:35:56.209874	1
2511	204	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.296669	2025-04-23 13:35:56.296672	1
2512	205	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.383115	2025-04-23 13:35:56.383119	1
2513	206	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.471693	2025-04-23 13:35:56.471698	1
2514	207	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.558787	2025-04-23 13:35:56.558791	1
2515	208	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.64927	2025-04-23 13:35:56.649274	1
2516	209	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.735774	2025-04-23 13:35:56.735777	1
2517	210	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.822809	2025-04-23 13:35:56.822813	1
2518	211	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.909589	2025-04-23 13:35:56.909593	1
2519	212	2025-04-05	\N	\N	present	\N	2025-04-23 13:35:56.996104	2025-04-23 13:35:56.996108	1
2785	214	2025-04-17	\N	\N	present	\N	2025-04-23 13:36:54.170544	2025-04-23 13:36:54.170547	1
2787	194	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:54.343985	2025-04-23 13:36:54.343989	1
2788	195	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:54.430958	2025-04-23 13:36:54.430963	1
2789	196	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:54.518519	2025-04-23 13:36:54.518522	1
2790	197	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:54.605158	2025-04-23 13:36:54.605161	1
2791	198	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:54.692037	2025-04-23 13:36:54.69204	1
2793	200	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:54.864876	2025-04-23 13:36:54.86488	1
2794	201	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:54.951515	2025-04-23 13:36:54.951519	1
2795	202	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.038034	2025-04-23 13:36:55.038038	1
2796	203	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.124378	2025-04-23 13:36:55.124382	1
2797	204	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.210824	2025-04-23 13:36:55.210828	1
2798	205	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.297823	2025-04-23 13:36:55.297827	1
2799	206	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.384129	2025-04-23 13:36:55.384132	1
2800	207	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.470959	2025-04-23 13:36:55.470962	1
2801	208	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.558688	2025-04-23 13:36:55.558692	1
2802	209	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.646838	2025-04-23 13:36:55.646841	1
2803	210	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.733287	2025-04-23 13:36:55.733291	1
2804	211	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.820535	2025-04-23 13:36:55.820539	1
2805	212	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:55.907529	2025-04-23 13:36:55.907532	1
2807	214	2025-04-18	\N	\N	present	\N	2025-04-23 13:36:56.080516	2025-04-23 13:36:56.080519	1
2809	194	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:56.253401	2025-04-23 13:36:56.253404	1
2810	195	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:56.339713	2025-04-23 13:36:56.339717	1
2811	196	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:56.426846	2025-04-23 13:36:56.426849	1
2812	197	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:56.513177	2025-04-23 13:36:56.51318	1
2813	198	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:56.599481	2025-04-23 13:36:56.599485	1
2815	200	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:56.773468	2025-04-23 13:36:56.773472	1
2816	201	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:56.860196	2025-04-23 13:36:56.8602	1
2817	202	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:56.96684	2025-04-23 13:36:56.966843	1
2818	203	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:57.053492	2025-04-23 13:36:57.053496	1
2819	204	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:57.139991	2025-04-23 13:36:57.140003	1
2820	205	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:57.226476	2025-04-23 13:36:57.22648	1
2821	206	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:57.312918	2025-04-23 13:36:57.312921	1
2822	207	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:57.399595	2025-04-23 13:36:57.399599	1
2823	208	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:57.487192	2025-04-23 13:36:57.487195	1
2824	209	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:57.574288	2025-04-23 13:36:57.574292	1
2825	210	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:57.666806	2025-04-23 13:36:57.666809	1
2826	211	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:57.753715	2025-04-23 13:36:57.753719	1
2827	212	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:57.840329	2025-04-23 13:36:57.840333	1
2829	214	2025-04-19	\N	\N	present	\N	2025-04-23 13:36:58.026669	2025-04-23 13:36:58.026673	1
2831	194	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:58.200358	2025-04-23 13:36:58.200363	1
2832	195	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:58.287055	2025-04-23 13:36:58.287058	1
2833	196	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:58.374225	2025-04-23 13:36:58.374229	1
2834	197	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:58.464037	2025-04-23 13:36:58.464042	1
2835	198	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:58.550637	2025-04-23 13:36:58.550641	1
2837	200	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:58.725958	2025-04-23 13:36:58.725962	1
2838	201	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:58.819482	2025-04-23 13:36:58.819486	1
2839	202	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:58.906314	2025-04-23 13:36:58.906317	1
2840	203	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:58.993217	2025-04-23 13:36:58.993221	1
2841	204	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:59.079774	2025-04-23 13:36:59.079778	1
2842	205	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:59.166569	2025-04-23 13:36:59.166573	1
2843	206	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:59.253645	2025-04-23 13:36:59.253649	1
2844	207	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:59.344043	2025-04-23 13:36:59.344047	1
2845	208	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:59.430973	2025-04-23 13:36:59.430976	1
2846	209	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:59.517772	2025-04-23 13:36:59.517776	1
2847	210	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:59.604318	2025-04-23 13:36:59.604322	1
2848	211	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:59.691032	2025-04-23 13:36:59.691036	1
2849	212	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:59.778251	2025-04-23 13:36:59.778255	1
2851	214	2025-04-20	\N	\N	present	\N	2025-04-23 13:36:59.952531	2025-04-23 13:36:59.952534	1
2853	194	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:00.126825	2025-04-23 13:37:00.12683	1
2854	195	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:00.214293	2025-04-23 13:37:00.214297	1
2855	196	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:00.301357	2025-04-23 13:37:00.301361	1
2856	197	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:00.388948	2025-04-23 13:37:00.388953	1
2857	198	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:00.481659	2025-04-23 13:37:00.481663	1
2859	200	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:00.656427	2025-04-23 13:37:00.65643	1
2860	201	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:00.743433	2025-04-23 13:37:00.743438	1
2861	202	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:00.831466	2025-04-23 13:37:00.831469	1
2862	203	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:00.918644	2025-04-23 13:37:00.918649	1
2863	204	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:01.005471	2025-04-23 13:37:01.005476	1
2864	205	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:01.092416	2025-04-23 13:37:01.09242	1
2865	206	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:01.179463	2025-04-23 13:37:01.179466	1
2866	207	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:01.266376	2025-04-23 13:37:01.26638	1
2867	208	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:01.353435	2025-04-23 13:37:01.353439	1
2868	209	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:01.440505	2025-04-23 13:37:01.440509	1
2869	210	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:01.527252	2025-04-23 13:37:01.527255	1
2870	211	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:01.614322	2025-04-23 13:37:01.614326	1
2871	212	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:01.701043	2025-04-23 13:37:01.701047	1
2873	214	2025-04-21	\N	\N	present	\N	2025-04-23 13:37:01.881115	2025-04-23 13:37:01.88112	1
2875	194	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:02.057368	2025-04-23 13:37:02.057372	1
2876	195	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:02.144261	2025-04-23 13:37:02.144265	1
2877	196	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:02.231672	2025-04-23 13:37:02.231675	1
2878	197	2025-04-22	\N	\N	present	\N	2025-04-23 13:37:02.319435	2025-04-23 13:37:02.31944	1
2900	197	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:04.247477	2025-04-23 13:37:04.247482	1
2901	198	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:04.334151	2025-04-23 13:37:04.334156	1
2903	200	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:04.508104	2025-04-23 13:37:04.508108	1
2904	201	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:04.595768	2025-04-23 13:37:04.595772	1
2905	202	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:04.682798	2025-04-23 13:37:04.682803	1
2906	203	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:04.769633	2025-04-23 13:37:04.769638	1
2907	204	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:04.859056	2025-04-23 13:37:04.85906	1
2908	205	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:04.947689	2025-04-23 13:37:04.947693	1
2909	206	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:05.035231	2025-04-23 13:37:05.035235	1
2910	207	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:05.121812	2025-04-23 13:37:05.121815	1
2911	208	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:05.208618	2025-04-23 13:37:05.208622	1
2912	209	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:05.295185	2025-04-23 13:37:05.295189	1
2913	210	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:05.381754	2025-04-23 13:37:05.381757	1
2914	211	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:05.468463	2025-04-23 13:37:05.468466	1
926	212	2025-04-23	\N	\N	present		2025-04-22 20:31:40.977881	2025-04-23 13:37:05.555748	1
2916	214	2025-04-23	\N	\N	present	\N	2025-04-23 13:37:05.735888	2025-04-23 13:37:05.735908	1
2918	216	2025-04-01	\N	\N	present	\N	2025-04-23 13:40:22.024948	2025-04-23 13:40:22.024955	1
2919	217	2025-04-01	\N	\N	present	\N	2025-04-23 13:40:22.132154	2025-04-23 13:40:22.13216	1
2920	218	2025-04-01	\N	\N	present	\N	2025-04-23 13:40:22.22206	2025-04-23 13:40:22.222067	1
2921	219	2025-04-01	\N	\N	present	\N	2025-04-23 13:40:22.310165	2025-04-23 13:40:22.310172	1
2922	220	2025-04-01	\N	\N	present	\N	2025-04-23 13:40:22.397201	2025-04-23 13:40:22.397207	1
2923	221	2025-04-01	\N	\N	present	\N	2025-04-23 13:40:22.484809	2025-04-23 13:40:22.484815	1
2924	222	2025-04-01	\N	\N	present	\N	2025-04-23 13:40:22.572383	2025-04-23 13:40:22.572389	1
2925	216	2025-04-02	\N	\N	present	\N	2025-04-23 13:40:22.659833	2025-04-23 13:40:22.659839	1
2926	217	2025-04-02	\N	\N	present	\N	2025-04-23 13:40:22.747378	2025-04-23 13:40:22.747384	1
2927	218	2025-04-02	\N	\N	present	\N	2025-04-23 13:40:22.838879	2025-04-23 13:40:22.838886	1
2928	219	2025-04-02	\N	\N	present	\N	2025-04-23 13:40:22.926373	2025-04-23 13:40:22.92638	1
2929	220	2025-04-02	\N	\N	present	\N	2025-04-23 13:40:23.013324	2025-04-23 13:40:23.01333	1
2930	221	2025-04-02	\N	\N	present	\N	2025-04-23 13:40:23.100378	2025-04-23 13:40:23.100385	1
2931	222	2025-04-02	\N	\N	present	\N	2025-04-23 13:40:23.18864	2025-04-23 13:40:23.188646	1
2932	216	2025-04-03	\N	\N	present	\N	2025-04-23 13:40:23.280664	2025-04-23 13:40:23.28067	1
2933	217	2025-04-03	\N	\N	present	\N	2025-04-23 13:40:23.368763	2025-04-23 13:40:23.368769	1
2934	218	2025-04-03	\N	\N	present	\N	2025-04-23 13:40:23.456231	2025-04-23 13:40:23.456237	1
2935	219	2025-04-03	\N	\N	present	\N	2025-04-23 13:40:23.548744	2025-04-23 13:40:23.54875	1
2936	220	2025-04-03	\N	\N	present	\N	2025-04-23 13:40:23.68318	2025-04-23 13:40:23.683186	1
2937	221	2025-04-03	\N	\N	present	\N	2025-04-23 13:40:23.770358	2025-04-23 13:40:23.770364	1
2938	222	2025-04-03	\N	\N	present	\N	2025-04-23 13:40:23.857693	2025-04-23 13:40:23.857699	1
2939	216	2025-04-04	\N	\N	present	\N	2025-04-23 13:40:23.94533	2025-04-23 13:40:23.945337	1
2940	217	2025-04-04	\N	\N	present	\N	2025-04-23 13:40:24.03265	2025-04-23 13:40:24.032656	1
2941	218	2025-04-04	\N	\N	present	\N	2025-04-23 13:40:24.120293	2025-04-23 13:40:24.120301	1
2942	219	2025-04-04	\N	\N	present	\N	2025-04-23 13:40:24.208612	2025-04-23 13:40:24.208618	1
2943	220	2025-04-04	\N	\N	present	\N	2025-04-23 13:40:24.296405	2025-04-23 13:40:24.296411	1
2944	221	2025-04-04	\N	\N	present	\N	2025-04-23 13:40:24.384607	2025-04-23 13:40:24.384613	1
2945	222	2025-04-04	\N	\N	present	\N	2025-04-23 13:40:24.471954	2025-04-23 13:40:24.471959	1
2946	216	2025-04-05	\N	\N	present	\N	2025-04-23 13:40:24.559026	2025-04-23 13:40:24.559032	1
2947	217	2025-04-05	\N	\N	present	\N	2025-04-23 13:40:24.646703	2025-04-23 13:40:24.646709	1
2948	218	2025-04-05	\N	\N	present	\N	2025-04-23 13:40:24.734605	2025-04-23 13:40:24.734611	1
2949	219	2025-04-05	\N	\N	present	\N	2025-04-23 13:40:24.822303	2025-04-23 13:40:24.82231	1
2950	220	2025-04-05	\N	\N	present	\N	2025-04-23 13:40:24.90951	2025-04-23 13:40:24.909516	1
2951	221	2025-04-05	\N	\N	present	\N	2025-04-23 13:40:24.99689	2025-04-23 13:40:24.996897	1
2952	222	2025-04-05	\N	\N	present	\N	2025-04-23 13:40:25.084345	2025-04-23 13:40:25.084351	1
2953	216	2025-04-06	\N	\N	present	\N	2025-04-23 13:40:25.172812	2025-04-23 13:40:25.173856	1
2954	217	2025-04-06	\N	\N	present	\N	2025-04-23 13:40:25.26184	2025-04-23 13:40:25.261846	1
2955	218	2025-04-06	\N	\N	present	\N	2025-04-23 13:40:25.34912	2025-04-23 13:40:25.349126	1
2956	219	2025-04-06	\N	\N	present	\N	2025-04-23 13:40:25.437337	2025-04-23 13:40:25.437344	1
2957	220	2025-04-06	\N	\N	present	\N	2025-04-23 13:40:25.528057	2025-04-23 13:40:25.528064	1
2958	221	2025-04-06	\N	\N	present	\N	2025-04-23 13:40:25.615228	2025-04-23 13:40:25.615235	1
2959	222	2025-04-06	\N	\N	present	\N	2025-04-23 13:40:25.702888	2025-04-23 13:40:25.702893	1
2960	216	2025-04-07	\N	\N	present	\N	2025-04-23 13:40:25.790143	2025-04-23 13:40:25.79015	1
2961	217	2025-04-07	\N	\N	present	\N	2025-04-23 13:40:25.881364	2025-04-23 13:40:25.88137	1
2962	218	2025-04-07	\N	\N	present	\N	2025-04-23 13:40:25.968979	2025-04-23 13:40:25.968985	1
2963	219	2025-04-07	\N	\N	present	\N	2025-04-23 13:40:26.056127	2025-04-23 13:40:26.056133	1
2964	220	2025-04-07	\N	\N	present	\N	2025-04-23 13:40:26.143774	2025-04-23 13:40:26.143781	1
2965	221	2025-04-07	\N	\N	present	\N	2025-04-23 13:40:26.230916	2025-04-23 13:40:26.230923	1
2966	222	2025-04-07	\N	\N	present	\N	2025-04-23 13:40:26.318222	2025-04-23 13:40:26.318228	1
2967	216	2025-04-08	\N	\N	present	\N	2025-04-23 13:40:26.405347	2025-04-23 13:40:26.405354	1
2968	217	2025-04-08	\N	\N	present	\N	2025-04-23 13:40:26.492682	2025-04-23 13:40:26.492688	1
2969	218	2025-04-08	\N	\N	present	\N	2025-04-23 13:40:26.580336	2025-04-23 13:40:26.580343	1
2970	219	2025-04-08	\N	\N	present	\N	2025-04-23 13:40:26.668521	2025-04-23 13:40:26.668527	1
2971	220	2025-04-08	\N	\N	present	\N	2025-04-23 13:40:26.755344	2025-04-23 13:40:26.75535	1
2972	221	2025-04-08	\N	\N	present	\N	2025-04-23 13:40:26.843298	2025-04-23 13:40:26.843305	1
2973	222	2025-04-08	\N	\N	present	\N	2025-04-23 13:40:26.931293	2025-04-23 13:40:26.931299	1
2974	216	2025-04-09	\N	\N	present	\N	2025-04-23 13:40:27.023749	2025-04-23 13:40:27.023756	1
2975	217	2025-04-09	\N	\N	present	\N	2025-04-23 13:40:27.111158	2025-04-23 13:40:27.111165	1
2976	218	2025-04-09	\N	\N	present	\N	2025-04-23 13:40:27.197984	2025-04-23 13:40:27.197991	1
2977	219	2025-04-09	\N	\N	present	\N	2025-04-23 13:40:27.28506	2025-04-23 13:40:27.285071	1
2978	220	2025-04-09	\N	\N	present	\N	2025-04-23 13:40:27.382003	2025-04-23 13:40:27.382009	1
2979	221	2025-04-09	\N	\N	present	\N	2025-04-23 13:40:27.469632	2025-04-23 13:40:27.469638	1
2980	222	2025-04-09	\N	\N	present	\N	2025-04-23 13:40:27.556836	2025-04-23 13:40:27.556842	1
2981	216	2025-04-10	\N	\N	present	\N	2025-04-23 13:40:27.645623	2025-04-23 13:40:27.645629	1
2982	217	2025-04-10	\N	\N	present	\N	2025-04-23 13:40:27.732839	2025-04-23 13:40:27.732845	1
2983	218	2025-04-10	\N	\N	present	\N	2025-04-23 13:40:27.820251	2025-04-23 13:40:27.820258	1
2984	219	2025-04-10	\N	\N	present	\N	2025-04-23 13:40:27.90864	2025-04-23 13:40:27.908646	1
2985	220	2025-04-10	\N	\N	present	\N	2025-04-23 13:40:27.996521	2025-04-23 13:40:27.996528	1
2986	221	2025-04-10	\N	\N	present	\N	2025-04-23 13:40:28.084078	2025-04-23 13:40:28.084084	1
2987	222	2025-04-10	\N	\N	present	\N	2025-04-23 13:40:28.174697	2025-04-23 13:40:28.174703	1
2988	216	2025-04-11	\N	\N	present	\N	2025-04-23 13:40:28.262681	2025-04-23 13:40:28.262687	1
2989	217	2025-04-11	\N	\N	present	\N	2025-04-23 13:40:28.349956	2025-04-23 13:40:28.349963	1
2990	218	2025-04-11	\N	\N	present	\N	2025-04-23 13:40:28.440661	2025-04-23 13:40:28.440667	1
2991	219	2025-04-11	\N	\N	present	\N	2025-04-23 13:40:28.528047	2025-04-23 13:40:28.528054	1
2992	220	2025-04-11	\N	\N	present	\N	2025-04-23 13:40:28.615627	2025-04-23 13:40:28.615634	1
2993	221	2025-04-11	\N	\N	present	\N	2025-04-23 13:40:28.703037	2025-04-23 13:40:28.703043	1
2994	222	2025-04-11	\N	\N	present	\N	2025-04-23 13:40:28.790928	2025-04-23 13:40:28.790934	1
2995	216	2025-04-12	\N	\N	present	\N	2025-04-23 13:40:28.882408	2025-04-23 13:40:28.882415	1
2996	217	2025-04-12	\N	\N	present	\N	2025-04-23 13:40:28.969475	2025-04-23 13:40:28.969481	1
2997	218	2025-04-12	\N	\N	present	\N	2025-04-23 13:40:29.057583	2025-04-23 13:40:29.057589	1
2998	219	2025-04-12	\N	\N	present	\N	2025-04-23 13:40:29.148023	2025-04-23 13:40:29.148029	1
2999	220	2025-04-12	\N	\N	present	\N	2025-04-23 13:40:29.236515	2025-04-23 13:40:29.236522	1
3000	221	2025-04-12	\N	\N	present	\N	2025-04-23 13:40:29.323611	2025-04-23 13:40:29.323618	1
3001	222	2025-04-12	\N	\N	present	\N	2025-04-23 13:40:29.410782	2025-04-23 13:40:29.410788	1
3005	219	2025-04-13	\N	\N	present	\N	2025-04-23 13:40:29.764924	2025-04-23 13:40:29.764931	1
3006	220	2025-04-13	\N	\N	present	\N	2025-04-23 13:40:29.851993	2025-04-23 13:40:29.851999	1
3007	221	2025-04-13	\N	\N	present	\N	2025-04-23 13:40:29.940057	2025-04-23 13:40:29.940064	1
3008	222	2025-04-13	\N	\N	present	\N	2025-04-23 13:40:30.027771	2025-04-23 13:40:30.027777	1
3009	216	2025-04-14	\N	\N	present	\N	2025-04-23 13:40:30.118563	2025-04-23 13:40:30.118569	1
3010	217	2025-04-14	\N	\N	present	\N	2025-04-23 13:40:30.205956	2025-04-23 13:40:30.205962	1
3011	218	2025-04-14	\N	\N	present	\N	2025-04-23 13:40:30.292799	2025-04-23 13:40:30.292805	1
3012	219	2025-04-14	\N	\N	present	\N	2025-04-23 13:40:30.381031	2025-04-23 13:40:30.381037	1
3013	220	2025-04-14	\N	\N	present	\N	2025-04-23 13:40:30.468796	2025-04-23 13:40:30.468802	1
3014	221	2025-04-14	\N	\N	present	\N	2025-04-23 13:40:30.557203	2025-04-23 13:40:30.55721	1
3015	222	2025-04-14	\N	\N	present	\N	2025-04-23 13:40:30.645085	2025-04-23 13:40:30.645091	1
3016	216	2025-04-15	\N	\N	present	\N	2025-04-23 13:40:30.732245	2025-04-23 13:40:30.732251	1
3017	217	2025-04-15	\N	\N	present	\N	2025-04-23 13:40:30.820081	2025-04-23 13:40:30.820087	1
3018	218	2025-04-15	\N	\N	present	\N	2025-04-23 13:40:30.906957	2025-04-23 13:40:30.906964	1
3019	219	2025-04-15	\N	\N	present	\N	2025-04-23 13:40:30.998308	2025-04-23 13:40:30.998314	1
3020	220	2025-04-15	\N	\N	present	\N	2025-04-23 13:40:31.087205	2025-04-23 13:40:31.087212	1
3021	221	2025-04-15	\N	\N	present	\N	2025-04-23 13:40:31.175659	2025-04-23 13:40:31.175666	1
3022	222	2025-04-15	\N	\N	present	\N	2025-04-23 13:40:31.263982	2025-04-23 13:40:31.263987	1
3023	216	2025-04-16	\N	\N	present	\N	2025-04-23 13:40:31.35189	2025-04-23 13:40:31.351897	1
3024	217	2025-04-16	\N	\N	present	\N	2025-04-23 13:40:31.442133	2025-04-23 13:40:31.442139	1
3025	218	2025-04-16	\N	\N	present	\N	2025-04-23 13:40:31.529265	2025-04-23 13:40:31.529271	1
3026	219	2025-04-16	\N	\N	present	\N	2025-04-23 13:40:31.616338	2025-04-23 13:40:31.616345	1
3027	220	2025-04-16	\N	\N	present	\N	2025-04-23 13:40:31.704468	2025-04-23 13:40:31.704475	1
3028	221	2025-04-16	\N	\N	present	\N	2025-04-23 13:40:31.791949	2025-04-23 13:40:31.791956	1
3029	222	2025-04-16	\N	\N	present	\N	2025-04-23 13:40:31.879552	2025-04-23 13:40:31.879558	1
3030	216	2025-04-17	\N	\N	present	\N	2025-04-23 13:40:31.968424	2025-04-23 13:40:31.968431	1
3031	217	2025-04-17	\N	\N	present	\N	2025-04-23 13:40:32.055996	2025-04-23 13:40:32.056002	1
3032	218	2025-04-17	\N	\N	present	\N	2025-04-23 13:40:32.143402	2025-04-23 13:40:32.143408	1
3033	219	2025-04-17	\N	\N	present	\N	2025-04-23 13:40:32.230909	2025-04-23 13:40:32.230915	1
3034	220	2025-04-17	\N	\N	present	\N	2025-04-23 13:40:32.318731	2025-04-23 13:40:32.318738	1
3035	221	2025-04-17	\N	\N	present	\N	2025-04-23 13:40:32.406231	2025-04-23 13:40:32.406237	1
3036	222	2025-04-17	\N	\N	present	\N	2025-04-23 13:40:32.493733	2025-04-23 13:40:32.493739	1
3037	216	2025-04-18	\N	\N	present	\N	2025-04-23 13:40:32.582258	2025-04-23 13:40:32.582265	1
3038	217	2025-04-18	\N	\N	present	\N	2025-04-23 13:40:32.670033	2025-04-23 13:40:32.67004	1
3039	218	2025-04-18	\N	\N	present	\N	2025-04-23 13:40:32.75729	2025-04-23 13:40:32.757296	1
3040	219	2025-04-18	\N	\N	present	\N	2025-04-23 13:40:32.844668	2025-04-23 13:40:32.844675	1
3041	220	2025-04-18	\N	\N	present	\N	2025-04-23 13:40:32.932293	2025-04-23 13:40:32.9323	1
3042	221	2025-04-18	\N	\N	present	\N	2025-04-23 13:40:33.020411	2025-04-23 13:40:33.020418	1
3043	222	2025-04-18	\N	\N	present	\N	2025-04-23 13:40:33.108313	2025-04-23 13:40:33.108318	1
3044	216	2025-04-19	\N	\N	present	\N	2025-04-23 13:40:33.196472	2025-04-23 13:40:33.196478	1
3045	217	2025-04-19	\N	\N	present	\N	2025-04-23 13:40:33.284705	2025-04-23 13:40:33.284711	1
3046	218	2025-04-19	\N	\N	present	\N	2025-04-23 13:40:33.37219	2025-04-23 13:40:33.372196	1
3047	219	2025-04-19	\N	\N	present	\N	2025-04-23 13:40:33.45938	2025-04-23 13:40:33.459386	1
3048	220	2025-04-19	\N	\N	present	\N	2025-04-23 13:40:33.549745	2025-04-23 13:40:33.549751	1
3049	221	2025-04-19	\N	\N	present	\N	2025-04-23 13:40:33.637895	2025-04-23 13:40:33.637901	1
3050	222	2025-04-19	\N	\N	present	\N	2025-04-23 13:40:33.725642	2025-04-23 13:40:33.725647	1
3051	216	2025-04-20	\N	\N	present	\N	2025-04-23 13:40:33.813102	2025-04-23 13:40:33.813108	1
3052	217	2025-04-20	\N	\N	present	\N	2025-04-23 13:40:33.900516	2025-04-23 13:40:33.900522	1
3053	218	2025-04-20	\N	\N	present	\N	2025-04-23 13:40:33.98862	2025-04-23 13:40:33.988627	1
3054	219	2025-04-20	\N	\N	present	\N	2025-04-23 13:40:34.080872	2025-04-23 13:40:34.080878	1
3055	220	2025-04-20	\N	\N	present	\N	2025-04-23 13:40:34.169595	2025-04-23 13:40:34.169602	1
3056	221	2025-04-20	\N	\N	present	\N	2025-04-23 13:40:34.266251	2025-04-23 13:40:34.266258	1
3057	222	2025-04-20	\N	\N	present	\N	2025-04-23 13:40:34.360732	2025-04-23 13:40:34.360737	1
3058	216	2025-04-21	\N	\N	present	\N	2025-04-23 13:40:34.448459	2025-04-23 13:40:34.448465	1
3059	217	2025-04-21	\N	\N	present	\N	2025-04-23 13:40:34.53673	2025-04-23 13:40:34.536737	1
3060	218	2025-04-21	\N	\N	present	\N	2025-04-23 13:40:34.6243	2025-04-23 13:40:34.624306	1
3061	219	2025-04-21	\N	\N	present	\N	2025-04-23 13:40:34.71197	2025-04-23 13:40:34.711977	1
3062	220	2025-04-21	\N	\N	present	\N	2025-04-23 13:40:34.808453	2025-04-23 13:40:34.80846	1
3063	221	2025-04-21	\N	\N	present	\N	2025-04-23 13:40:34.898754	2025-04-23 13:40:34.89876	1
3064	222	2025-04-21	\N	\N	present	\N	2025-04-23 13:40:34.986164	2025-04-23 13:40:34.98617	1
3065	216	2025-04-22	\N	\N	present	\N	2025-04-23 13:40:35.074688	2025-04-23 13:40:35.074695	1
3066	217	2025-04-22	\N	\N	present	\N	2025-04-23 13:40:35.161993	2025-04-23 13:40:35.161999	1
3067	218	2025-04-22	\N	\N	present	\N	2025-04-23 13:40:35.249421	2025-04-23 13:40:35.249427	1
3068	219	2025-04-22	\N	\N	present	\N	2025-04-23 13:40:35.336647	2025-04-23 13:40:35.336654	1
3069	220	2025-04-22	\N	\N	present	\N	2025-04-23 13:40:35.424447	2025-04-23 13:40:35.424454	1
3070	221	2025-04-22	\N	\N	present	\N	2025-04-23 13:40:35.512374	2025-04-23 13:40:35.512381	1
3071	222	2025-04-22	\N	\N	present	\N	2025-04-23 13:40:35.6015	2025-04-23 13:40:35.601506	1
3072	216	2025-04-23	\N	\N	present	\N	2025-04-23 13:40:35.688684	2025-04-23 13:40:35.68869	1
3073	217	2025-04-23	\N	\N	present	\N	2025-04-23 13:40:35.777757	2025-04-23 13:40:35.777764	1
3074	218	2025-04-23	\N	\N	present	\N	2025-04-23 13:40:35.865327	2025-04-23 13:40:35.865333	1
3075	219	2025-04-23	\N	\N	present	\N	2025-04-23 13:40:35.952657	2025-04-23 13:40:35.952663	1
3076	220	2025-04-23	\N	\N	present	\N	2025-04-23 13:40:36.040876	2025-04-23 13:40:36.040882	1
3077	221	2025-04-23	\N	\N	present	\N	2025-04-23 13:40:36.128748	2025-04-23 13:40:36.128754	1
3078	222	2025-04-23	\N	\N	present	\N	2025-04-23 13:40:36.217893	2025-04-23 13:40:36.217899	1
3079	184	2025-04-24	\N	\N	present	\N	2025-04-24 19:03:57.54293	2025-04-24 19:03:57.542935	1
3080	185	2025-04-24	\N	\N	present	\N	2025-04-24 19:03:57.647196	2025-04-24 19:03:57.647201	1
3081	186	2025-04-24	\N	\N	present	\N	2025-04-24 19:03:57.741147	2025-04-24 19:03:57.741151	1
3082	187	2025-04-24	\N	\N	present	\N	2025-04-24 19:03:57.833737	2025-04-24 19:03:57.833742	1
3083	188	2025-04-24	\N	\N	present	\N	2025-04-24 19:03:57.931285	2025-04-24 19:03:57.93129	1
3085	180	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:25.674705	2025-04-24 19:04:25.67471	1
3086	181	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:25.76655	2025-04-24 19:04:25.766554	1
3087	179	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:25.858466	2025-04-24 19:04:25.85847	1
3088	178	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:25.95233	2025-04-24 19:04:25.952334	1
3089	183	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:26.044115	2025-04-24 19:04:26.04412	1
3090	182	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:26.137122	2025-04-24 19:04:26.137127	1
3091	175	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:26.2297	2025-04-24 19:04:26.229705	1
3092	173	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:26.321448	2025-04-24 19:04:26.321452	1
3093	172	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:26.413496	2025-04-24 19:04:26.413501	1
3095	171	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:26.597358	2025-04-24 19:04:26.597362	1
3096	174	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:26.689356	2025-04-24 19:04:26.68936	1
3097	177	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:26.781126	2025-04-24 19:04:26.78113	1
3098	169	2025-04-24	\N	\N	present	\N	2025-04-24 19:04:26.873069	2025-04-24 19:04:26.873074	1
3100	193	2025-04-24	\N	\N	present	\N	2025-04-24 19:05:37.838334	2025-04-24 19:05:37.838338	1
3101	191	2025-04-24	\N	\N	present	\N	2025-04-24 19:05:37.930582	2025-04-24 19:05:37.930587	1
3102	189	2025-04-24	\N	\N	present	\N	2025-04-24 19:05:38.0238	2025-04-24 19:05:38.023805	1
3103	190	2025-04-24	\N	\N	present	\N	2025-04-24 19:05:38.116259	2025-04-24 19:05:38.116263	1
3104	192	2025-04-24	\N	\N	present	\N	2025-04-24 19:05:38.208235	2025-04-24 19:05:38.208239	1
3105	194	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:16.323429	2025-04-24 19:06:16.323433	1
3106	195	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:16.415737	2025-04-24 19:06:16.415741	1
3107	196	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:16.510064	2025-04-24 19:06:16.510068	1
3108	197	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:16.612198	2025-04-24 19:06:16.612202	1
3120	209	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:17.739265	2025-04-24 19:06:17.739269	1
3121	210	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:17.835993	2025-04-24 19:06:17.835997	1
3122	211	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:17.928595	2025-04-24 19:06:17.9286	1
3123	212	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:18.023106	2025-04-24 19:06:18.02311	1
3125	214	2025-04-24	\N	\N	present	\N	2025-04-24 19:06:18.2145	2025-04-24 19:06:18.214504	1
3127	184	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:40.946469	2025-04-25 13:58:40.946474	1
3128	185	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:41.047197	2025-04-25 13:58:41.047201	1
3129	186	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:41.134714	2025-04-25 13:58:41.134719	1
3130	187	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:41.222667	2025-04-25 13:58:41.222672	1
3131	188	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:41.309955	2025-04-25 13:58:41.309961	1
3133	180	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:55.440207	2025-04-25 13:58:55.440212	1
3134	181	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:55.526944	2025-04-25 13:58:55.526949	1
3135	179	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:55.613383	2025-04-25 13:58:55.613388	1
3136	178	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:55.699786	2025-04-25 13:58:55.69979	1
3137	183	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:55.789958	2025-04-25 13:58:55.789964	1
3138	182	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:55.878007	2025-04-25 13:58:55.878011	1
3139	175	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:55.968119	2025-04-25 13:58:55.968124	1
3140	173	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:56.054775	2025-04-25 13:58:56.054779	1
3141	172	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:56.14813	2025-04-25 13:58:56.148134	1
3143	171	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:56.337374	2025-04-25 13:58:56.337378	1
3144	174	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:56.427582	2025-04-25 13:58:56.427587	1
3145	177	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:56.523485	2025-04-25 13:58:56.52349	1
3146	169	2025-04-25	\N	\N	present	\N	2025-04-25 13:58:56.615285	2025-04-25 13:58:56.61529	1
3148	193	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:23.365344	2025-04-25 13:59:23.365349	1
3149	191	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:23.454522	2025-04-25 13:59:23.454526	1
3150	189	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:23.541498	2025-04-25 13:59:23.541503	1
3151	190	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:23.629161	2025-04-25 13:59:23.629166	1
3152	192	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:23.717281	2025-04-25 13:59:23.717285	1
3153	216	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:40.383641	2025-04-25 13:59:40.383646	1
3154	217	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:40.470612	2025-04-25 13:59:40.470617	1
3155	218	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:40.558042	2025-04-25 13:59:40.558047	1
3156	219	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:40.645851	2025-04-25 13:59:40.645855	1
3157	220	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:40.736281	2025-04-25 13:59:40.736286	1
3158	221	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:40.823361	2025-04-25 13:59:40.823366	1
3159	222	2025-04-25	\N	\N	present	\N	2025-04-25 13:59:40.913886	2025-04-25 13:59:40.91389	1
3160	184	2025-04-26	\N	\N	present	\N	2025-04-26 16:46:44.281628	2025-04-26 16:46:44.281633	1
3161	185	2025-04-26	\N	\N	present	\N	2025-04-26 16:46:44.382103	2025-04-26 16:46:44.382108	1
3162	186	2025-04-26	\N	\N	present	\N	2025-04-26 16:46:44.471217	2025-04-26 16:46:44.471222	1
3163	187	2025-04-26	\N	\N	present	\N	2025-04-26 16:46:44.561622	2025-04-26 16:46:44.561628	1
3164	188	2025-04-26	\N	\N	present	\N	2025-04-26 16:46:44.650823	2025-04-26 16:46:44.650828	1
3165	180	2025-04-26	\N	\N	present	\N	2025-04-26 16:46:59.71191	2025-04-26 16:46:59.711915	1
3166	181	2025-04-26	\N	\N	present	\N	2025-04-26 16:46:59.80262	2025-04-26 16:46:59.802625	1
3167	179	2025-04-26	\N	\N	present	\N	2025-04-26 16:46:59.894241	2025-04-26 16:46:59.894247	1
3168	178	2025-04-26	\N	\N	present	\N	2025-04-26 16:46:59.982681	2025-04-26 16:46:59.982686	1
3169	183	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:00.071416	2025-04-26 16:47:00.071421	1
3170	182	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:00.16114	2025-04-26 16:47:00.161146	1
3171	175	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:00.255444	2025-04-26 16:47:00.255449	1
3172	173	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:00.343967	2025-04-26 16:47:00.343972	1
3173	172	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:00.43596	2025-04-26 16:47:00.435965	1
3175	171	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:00.615043	2025-04-26 16:47:00.615047	1
3176	174	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:00.705577	2025-04-26 16:47:00.705581	1
3177	177	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:00.794758	2025-04-26 16:47:00.794763	1
3178	169	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:00.887627	2025-04-26 16:47:00.887631	1
3181	193	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:17.889331	2025-04-26 16:47:17.889336	1
3182	191	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:17.985616	2025-04-26 16:47:17.985621	1
3183	189	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:18.081533	2025-04-26 16:47:18.08154	1
3184	190	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:18.171132	2025-04-26 16:47:18.171138	1
3185	192	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:18.266809	2025-04-26 16:47:18.266814	1
3186	194	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:31.258061	2025-04-26 16:47:31.258066	1
3187	195	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:31.349453	2025-04-26 16:47:31.349458	1
3189	197	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:31.527125	2025-04-26 16:47:31.52713	1
3191	200	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:31.704692	2025-04-26 16:47:31.704697	1
3192	202	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:31.794023	2025-04-26 16:47:31.794028	1
3193	203	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:31.88854	2025-04-26 16:47:31.888545	1
3194	205	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:31.977113	2025-04-26 16:47:31.977118	1
3195	206	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:32.066208	2025-04-26 16:47:32.066213	1
3196	207	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:32.15529	2025-04-26 16:47:32.155294	1
3197	208	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:32.244529	2025-04-26 16:47:32.244534	1
3198	209	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:32.333479	2025-04-26 16:47:32.333484	1
3199	210	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:32.422642	2025-04-26 16:47:32.422647	1
3200	212	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:32.511257	2025-04-26 16:47:32.511262	1
3201	198	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:32.599881	2025-04-26 16:47:32.599886	1
3202	201	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:32.68941	2025-04-26 16:47:32.689416	1
3203	204	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:32.78475	2025-04-26 16:47:32.784755	1
3205	211	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:32.968175	2025-04-26 16:47:32.96818	1
3206	214	2025-04-26	\N	\N	present	\N	2025-04-26 16:47:33.058681	2025-04-26 16:47:33.058686	1
3208	216	2025-04-26	\N	\N	present	\N	2025-04-26 16:48:12.379707	2025-04-26 16:48:12.379712	1
3209	217	2025-04-26	\N	\N	present	\N	2025-04-26 16:48:12.473094	2025-04-26 16:48:12.473098	1
3210	218	2025-04-26	\N	\N	present	\N	2025-04-26 16:48:12.565266	2025-04-26 16:48:12.565271	1
3211	219	2025-04-26	\N	\N	present	\N	2025-04-26 16:48:12.654221	2025-04-26 16:48:12.654227	1
3212	220	2025-04-26	\N	\N	present	\N	2025-04-26 16:48:12.742436	2025-04-26 16:48:12.742441	1
3213	221	2025-04-26	\N	\N	present	\N	2025-04-26 16:48:12.831711	2025-04-26 16:48:12.831716	1
3214	222	2025-04-26	\N	\N	present	\N	2025-04-26 16:48:12.920313	2025-04-26 16:48:12.920318	1
3215	184	2025-04-27	\N	\N	present	\N	2025-04-27 10:24:51.340809	2025-04-27 10:24:51.340814	1
3188	196	2025-04-26	\N	\N	absent		2025-04-26 16:47:31.438325	2025-04-30 11:01:05.89309	1
3226	175	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:28.040226	2025-04-27 10:25:28.040231	1
3227	173	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:28.126143	2025-04-27 10:25:28.126149	1
3228	172	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:28.212234	2025-04-27 10:25:28.212239	1
3230	171	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:28.383796	2025-04-27 10:25:28.383801	1
3231	174	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:28.469694	2025-04-27 10:25:28.469699	1
3232	177	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:28.555649	2025-04-27 10:25:28.555654	1
3233	169	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:28.641651	2025-04-27 10:25:28.641656	1
3236	193	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:58.152104	2025-04-27 10:25:58.152109	1
3237	191	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:58.238604	2025-04-27 10:25:58.238609	1
3238	189	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:58.325259	2025-04-27 10:25:58.325265	1
3239	190	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:58.411816	2025-04-27 10:25:58.411821	1
3240	192	2025-04-27	\N	\N	present	\N	2025-04-27 10:25:58.498555	2025-04-27 10:25:58.49856	1
3241	194	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:41.768229	2025-04-27 10:27:41.768234	1
3242	195	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:41.870657	2025-04-27 10:27:41.870662	1
3243	196	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:41.967636	2025-04-27 10:27:41.967641	1
3244	197	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:42.062645	2025-04-27 10:27:42.06265	1
3246	200	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:42.253094	2025-04-27 10:27:42.253099	1
3247	202	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:42.355096	2025-04-27 10:27:42.355102	1
3248	203	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:42.44937	2025-04-27 10:27:42.449375	1
3249	205	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:42.544084	2025-04-27 10:27:42.544089	1
3250	206	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:42.637649	2025-04-27 10:27:42.637654	1
3251	207	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:42.731452	2025-04-27 10:27:42.731457	1
3252	208	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:42.825628	2025-04-27 10:27:42.825632	1
3253	209	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:42.920319	2025-04-27 10:27:42.920324	1
3254	210	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:43.013723	2025-04-27 10:27:43.013728	1
3255	198	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:43.108567	2025-04-27 10:27:43.108574	1
3256	201	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:43.202584	2025-04-27 10:27:43.202589	1
3257	204	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:43.296423	2025-04-27 10:27:43.296429	1
3259	212	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:43.488163	2025-04-27 10:27:43.488169	1
3260	211	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:43.581552	2025-04-27 10:27:43.581556	1
3261	214	2025-04-27	\N	\N	present	\N	2025-04-27 10:27:43.67561	2025-04-27 10:27:43.675635	1
3263	216	2025-04-27	\N	\N	present	\N	2025-04-27 10:28:27.23524	2025-04-27 10:28:27.235246	1
3264	217	2025-04-27	\N	\N	present	\N	2025-04-27 10:28:27.333607	2025-04-27 10:28:27.333613	1
3265	218	2025-04-27	\N	\N	present	\N	2025-04-27 10:28:27.438586	2025-04-27 10:28:27.43859	1
3266	219	2025-04-27	\N	\N	present	\N	2025-04-27 10:28:27.53287	2025-04-27 10:28:27.532875	1
3267	220	2025-04-27	\N	\N	present	\N	2025-04-27 10:28:27.627259	2025-04-27 10:28:27.627265	1
3268	221	2025-04-27	\N	\N	present	\N	2025-04-27 10:28:27.728556	2025-04-27 10:28:27.728561	1
3269	222	2025-04-27	\N	\N	present	\N	2025-04-27 10:28:27.829239	2025-04-27 10:28:27.829244	1
3270	184	2025-04-28	\N	\N	present	\N	2025-04-28 08:47:13.38744	2025-04-28 08:47:13.387445	1
3271	185	2025-04-28	\N	\N	present	\N	2025-04-28 08:47:13.481112	2025-04-28 08:47:13.481116	1
3272	186	2025-04-28	\N	\N	present	\N	2025-04-28 08:47:13.567393	2025-04-28 08:47:13.567397	1
3273	187	2025-04-28	\N	\N	present	\N	2025-04-28 08:47:13.655259	2025-04-28 08:47:13.655264	1
3274	188	2025-04-28	\N	\N	present	\N	2025-04-28 08:47:13.743357	2025-04-28 08:47:13.743361	1
3275	180	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:03.707962	2025-04-28 08:48:03.707977	1
3276	181	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:03.79611	2025-04-28 08:48:03.796114	1
3277	179	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:03.885477	2025-04-28 08:48:03.885482	1
3278	178	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:03.972401	2025-04-28 08:48:03.972406	1
3279	183	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:04.060944	2025-04-28 08:48:04.060948	1
3280	182	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:04.148399	2025-04-28 08:48:04.148404	1
3281	175	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:04.235601	2025-04-28 08:48:04.235605	1
3282	173	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:04.321801	2025-04-28 08:48:04.321805	1
3283	172	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:04.408633	2025-04-28 08:48:04.408638	1
3285	171	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:04.582238	2025-04-28 08:48:04.582243	1
3286	174	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:04.668917	2025-04-28 08:48:04.668921	1
3287	177	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:04.755801	2025-04-28 08:48:04.755806	1
3288	169	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:04.842155	2025-04-28 08:48:04.842158	1
3291	193	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:17.932009	2025-04-28 08:48:17.932013	1
3292	191	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:18.019323	2025-04-28 08:48:18.019327	1
3293	189	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:18.105744	2025-04-28 08:48:18.105749	1
3294	190	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:18.192266	2025-04-28 08:48:18.19227	1
3295	192	2025-04-28	\N	\N	present	\N	2025-04-28 08:48:18.279594	2025-04-28 08:48:18.279599	1
3296	194	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:17.169785	2025-04-28 08:49:17.169789	1
3297	195	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:17.256741	2025-04-28 08:49:17.256745	1
3298	196	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:17.343845	2025-04-28 08:49:17.34385	1
3299	197	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:17.430455	2025-04-28 08:49:17.43046	1
3301	200	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:17.602765	2025-04-28 08:49:17.602769	1
3302	202	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:17.689942	2025-04-28 08:49:17.689946	1
3303	203	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:17.777338	2025-04-28 08:49:17.777343	1
3304	205	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:17.864455	2025-04-28 08:49:17.86446	1
3305	206	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:17.950943	2025-04-28 08:49:17.950947	1
3306	207	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:18.037107	2025-04-28 08:49:18.037111	1
3307	208	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:18.123843	2025-04-28 08:49:18.123848	1
3308	209	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:18.210425	2025-04-28 08:49:18.210429	1
3309	210	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:18.297081	2025-04-28 08:49:18.297095	1
3310	198	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:18.383262	2025-04-28 08:49:18.383266	1
3311	201	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:18.469319	2025-04-28 08:49:18.469323	1
3312	204	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:18.555552	2025-04-28 08:49:18.555556	1
3314	212	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:18.729159	2025-04-28 08:49:18.729163	1
3315	211	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:18.815983	2025-04-28 08:49:18.815987	1
3316	214	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:18.903742	2025-04-28 08:49:18.903746	1
3318	216	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:35.233027	2025-04-28 08:49:35.233031	1
3319	217	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:35.321695	2025-04-28 08:49:35.321699	1
3320	218	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:35.408315	2025-04-28 08:49:35.40832	1
3321	219	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:35.495008	2025-04-28 08:49:35.495013	1
3322	220	2025-04-28	\N	\N	present	\N	2025-04-28 08:49:35.581539	2025-04-28 08:49:35.581543	1
3332	179	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:39.31255	2025-04-29 22:11:39.312553	1
3333	178	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:39.405974	2025-04-29 22:11:39.405977	1
3334	183	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:39.500763	2025-04-29 22:11:39.500766	1
3335	182	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:39.593949	2025-04-29 22:11:39.593953	1
3336	175	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:39.684614	2025-04-29 22:11:39.684617	1
3337	173	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:39.773861	2025-04-29 22:11:39.773865	1
3338	172	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:39.863529	2025-04-29 22:11:39.863533	1
3340	171	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:40.048096	2025-04-29 22:11:40.048099	1
3341	174	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:40.14128	2025-04-29 22:11:40.141283	1
3342	177	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:40.229533	2025-04-29 22:11:40.229536	1
3343	169	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:40.318708	2025-04-29 22:11:40.318712	1
3346	193	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:52.789568	2025-04-29 22:11:52.789573	1
3347	191	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:52.878598	2025-04-29 22:11:52.878602	1
3348	189	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:52.967906	2025-04-29 22:11:52.96791	1
3349	190	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:53.063878	2025-04-29 22:11:53.063883	1
3350	192	2025-04-29	\N	\N	present	\N	2025-04-29 22:11:53.154915	2025-04-29 22:11:53.154923	1
3351	194	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:10.18059	2025-04-29 22:12:10.180594	1
3352	195	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:10.270447	2025-04-29 22:12:10.270452	1
3353	196	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:10.359591	2025-04-29 22:12:10.359596	1
3354	197	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:10.448135	2025-04-29 22:12:10.448139	1
3356	200	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:10.63468	2025-04-29 22:12:10.634684	1
3357	202	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:10.728624	2025-04-29 22:12:10.728628	1
3358	203	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:10.823868	2025-04-29 22:12:10.823872	1
3359	205	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:10.914501	2025-04-29 22:12:10.914504	1
3360	206	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:11.057268	2025-04-29 22:12:11.057272	1
3361	207	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:11.147063	2025-04-29 22:12:11.147067	1
3362	208	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:11.240749	2025-04-29 22:12:11.240752	1
3363	209	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:11.343209	2025-04-29 22:12:11.343214	1
3364	210	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:11.433014	2025-04-29 22:12:11.433018	1
3365	198	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:11.523802	2025-04-29 22:12:11.523806	1
3366	201	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:11.613222	2025-04-29 22:12:11.613227	1
3367	204	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:11.710806	2025-04-29 22:12:11.71081	1
3369	212	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:11.903321	2025-04-29 22:12:11.903326	1
3370	214	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:12.005911	2025-04-29 22:12:12.005925	1
3371	211	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:12.100588	2025-04-29 22:12:12.100593	1
3372	216	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:33.31665	2025-04-29 22:12:33.316655	1
3373	217	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:33.405779	2025-04-29 22:12:33.405782	1
3374	218	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:33.530359	2025-04-29 22:12:33.530363	1
3375	219	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:33.628632	2025-04-29 22:12:33.628635	1
3376	220	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:33.717838	2025-04-29 22:12:33.717842	1
3377	221	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:33.809696	2025-04-29 22:12:33.809699	1
3378	222	2025-04-29	\N	\N	present	\N	2025-04-29 22:12:33.909241	2025-04-29 22:12:33.909244	1
3379	184	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:26.345458	2025-04-30 10:32:26.345463	1
3380	185	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:26.452749	2025-04-30 10:32:26.452754	1
3381	186	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:26.54554	2025-04-30 10:32:26.545545	1
3382	187	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:26.637033	2025-04-30 10:32:26.637038	1
3383	188	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:26.728811	2025-04-30 10:32:26.728815	1
3384	180	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:38.682623	2025-04-30 10:32:38.682628	1
3385	181	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:38.772573	2025-04-30 10:32:38.772578	1
3386	179	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:38.863864	2025-04-30 10:32:38.863869	1
3387	178	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:38.955846	2025-04-30 10:32:38.955852	1
3388	183	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:39.045877	2025-04-30 10:32:39.045882	1
3389	182	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:39.137191	2025-04-30 10:32:39.137196	1
3390	175	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:39.226974	2025-04-30 10:32:39.226979	1
3391	173	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:39.315876	2025-04-30 10:32:39.315881	1
3392	172	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:39.410592	2025-04-30 10:32:39.410597	1
3394	171	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:39.631004	2025-04-30 10:32:39.631009	1
3395	174	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:39.720912	2025-04-30 10:32:39.720917	1
3396	177	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:39.819926	2025-04-30 10:32:39.819931	1
3397	169	2025-04-30	\N	\N	present	\N	2025-04-30 10:32:39.926662	2025-04-30 10:32:39.926666	1
3400	193	2025-04-30	\N	\N	present	\N	2025-04-30 10:33:21.601751	2025-04-30 10:33:21.601756	1
3401	191	2025-04-30	\N	\N	present	\N	2025-04-30 10:33:21.691804	2025-04-30 10:33:21.691809	1
3402	189	2025-04-30	\N	\N	present	\N	2025-04-30 10:33:21.783248	2025-04-30 10:33:21.783253	1
3403	190	2025-04-30	\N	\N	present	\N	2025-04-30 10:33:21.874783	2025-04-30 10:33:21.874788	1
3404	192	2025-04-30	\N	\N	present	\N	2025-04-30 10:33:21.967448	2025-04-30 10:33:21.967452	1
3405	194	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:49.23763	2025-04-30 10:34:49.237635	1
3406	195	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:49.328483	2025-04-30 10:34:49.328488	1
3407	196	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:49.416949	2025-04-30 10:34:49.416954	1
3408	197	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:49.50648	2025-04-30 10:34:49.506487	1
3410	200	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:49.684909	2025-04-30 10:34:49.684914	1
3411	202	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:49.773284	2025-04-30 10:34:49.773289	1
3412	203	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:49.863654	2025-04-30 10:34:49.863658	1
3413	205	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:49.952511	2025-04-30 10:34:49.952515	1
3414	206	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:50.04137	2025-04-30 10:34:50.041375	1
3415	207	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:50.129577	2025-04-30 10:34:50.129583	1
3416	208	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:50.2206	2025-04-30 10:34:50.220605	1
3417	209	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:50.309798	2025-04-30 10:34:50.309803	1
3418	210	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:50.398229	2025-04-30 10:34:50.398234	1
3419	198	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:50.489717	2025-04-30 10:34:50.489722	1
3420	201	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:50.578209	2025-04-30 10:34:50.578214	1
3421	204	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:50.666534	2025-04-30 10:34:50.66654	1
3423	212	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:50.842086	2025-04-30 10:34:50.84209	1
3424	214	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:50.930026	2025-04-30 10:34:50.930031	1
3425	211	2025-04-30	\N	\N	present	\N	2025-04-30 10:34:51.018052	2025-04-30 10:34:51.018057	1
3426	216	2025-04-30	\N	\N	present	\N	2025-04-30 10:35:09.240454	2025-04-30 10:35:09.240459	1
3427	217	2025-04-30	\N	\N	present	\N	2025-04-30 10:35:09.328986	2025-04-30 10:35:09.32899	1
3428	218	2025-04-30	\N	\N	present	\N	2025-04-30 10:35:09.420439	2025-04-30 10:35:09.420443	1
3429	219	2025-04-30	\N	\N	present	\N	2025-04-30 10:35:09.510576	2025-04-30 10:35:09.510581	1
3437	188	2025-05-01	\N	\N	present	\N	2025-05-08 19:08:37.955076	2025-05-08 19:08:37.95508	1
3438	184	2025-05-02	\N	\N	present	\N	2025-05-08 19:08:38.055451	2025-05-08 19:08:38.055456	1
3439	185	2025-05-02	\N	\N	present	\N	2025-05-08 19:08:38.14514	2025-05-08 19:08:38.145144	1
3440	186	2025-05-02	\N	\N	present	\N	2025-05-08 19:08:38.234905	2025-05-08 19:08:38.234909	1
3441	187	2025-05-02	\N	\N	present	\N	2025-05-08 19:08:38.327509	2025-05-08 19:08:38.327513	1
3442	188	2025-05-02	\N	\N	present	\N	2025-05-08 19:08:38.417118	2025-05-08 19:08:38.417122	1
3443	184	2025-05-03	\N	\N	present	\N	2025-05-08 19:08:38.511503	2025-05-08 19:08:38.511507	1
3444	185	2025-05-03	\N	\N	present	\N	2025-05-08 19:08:38.602537	2025-05-08 19:08:38.602542	1
3445	186	2025-05-03	\N	\N	present	\N	2025-05-08 19:08:38.691811	2025-05-08 19:08:38.691815	1
3446	187	2025-05-03	\N	\N	present	\N	2025-05-08 19:08:38.781371	2025-05-08 19:08:38.781376	1
3447	188	2025-05-03	\N	\N	present	\N	2025-05-08 19:08:38.870989	2025-05-08 19:08:38.870994	1
3448	184	2025-05-04	\N	\N	present	\N	2025-05-08 19:08:38.961222	2025-05-08 19:08:38.961226	1
3449	185	2025-05-04	\N	\N	present	\N	2025-05-08 19:08:39.050915	2025-05-08 19:08:39.05092	1
3450	186	2025-05-04	\N	\N	present	\N	2025-05-08 19:08:39.141173	2025-05-08 19:08:39.141177	1
3451	187	2025-05-04	\N	\N	present	\N	2025-05-08 19:08:39.23104	2025-05-08 19:08:39.231045	1
3452	188	2025-05-04	\N	\N	present	\N	2025-05-08 19:08:39.323698	2025-05-08 19:08:39.323702	1
3453	184	2025-05-05	\N	\N	present	\N	2025-05-08 19:08:39.41912	2025-05-08 19:08:39.419125	1
3454	185	2025-05-05	\N	\N	present	\N	2025-05-08 19:08:39.518532	2025-05-08 19:08:39.518537	1
3455	186	2025-05-05	\N	\N	present	\N	2025-05-08 19:08:39.61187	2025-05-08 19:08:39.611875	1
3456	187	2025-05-05	\N	\N	present	\N	2025-05-08 19:08:39.702198	2025-05-08 19:08:39.702202	1
3457	188	2025-05-05	\N	\N	present	\N	2025-05-08 19:08:39.791442	2025-05-08 19:08:39.791446	1
3458	184	2025-05-06	\N	\N	present	\N	2025-05-08 19:08:39.886703	2025-05-08 19:08:39.886707	1
3459	185	2025-05-06	\N	\N	present	\N	2025-05-08 19:08:39.979761	2025-05-08 19:08:39.979765	1
3460	186	2025-05-06	\N	\N	present	\N	2025-05-08 19:08:40.072361	2025-05-08 19:08:40.072366	1
3461	187	2025-05-06	\N	\N	present	\N	2025-05-08 19:08:40.161989	2025-05-08 19:08:40.161994	1
3462	188	2025-05-06	\N	\N	present	\N	2025-05-08 19:08:40.251346	2025-05-08 19:08:40.25135	1
3463	184	2025-05-07	\N	\N	present	\N	2025-05-08 19:08:40.363793	2025-05-08 19:08:40.363797	1
3464	185	2025-05-07	\N	\N	present	\N	2025-05-08 19:08:40.463614	2025-05-08 19:08:40.463618	1
3465	186	2025-05-07	\N	\N	present	\N	2025-05-08 19:08:40.55337	2025-05-08 19:08:40.553375	1
3466	187	2025-05-07	\N	\N	present	\N	2025-05-08 19:08:40.642667	2025-05-08 19:08:40.642671	1
3467	188	2025-05-07	\N	\N	present	\N	2025-05-08 19:08:40.741919	2025-05-08 19:08:40.741923	1
3468	184	2025-05-08	\N	\N	present	\N	2025-05-08 19:08:40.8357	2025-05-08 19:08:40.835704	1
3469	185	2025-05-08	\N	\N	present	\N	2025-05-08 19:08:40.927382	2025-05-08 19:08:40.927386	1
3470	186	2025-05-08	\N	\N	present	\N	2025-05-08 19:08:41.019282	2025-05-08 19:08:41.019287	1
3471	187	2025-05-08	\N	\N	present	\N	2025-05-08 19:08:41.116257	2025-05-08 19:08:41.116262	1
3472	188	2025-05-08	\N	\N	present	\N	2025-05-08 19:08:41.206196	2025-05-08 19:08:41.2062	1
3473	180	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:08.989838	2025-05-08 19:09:08.989842	1
3474	181	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:09.08088	2025-05-08 19:09:09.080884	1
3475	179	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:09.170837	2025-05-08 19:09:09.170842	1
3476	178	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:09.260639	2025-05-08 19:09:09.260643	1
3477	183	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:09.350325	2025-05-08 19:09:09.350329	1
3478	182	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:09.440308	2025-05-08 19:09:09.440312	1
3479	175	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:09.529999	2025-05-08 19:09:09.530004	1
3480	173	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:09.619085	2025-05-08 19:09:09.61909	1
3481	172	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:09.711679	2025-05-08 19:09:09.711683	1
3483	171	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:09.892759	2025-05-08 19:09:09.892763	1
3484	174	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:09.982854	2025-05-08 19:09:09.982858	1
3485	177	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:10.07242	2025-05-08 19:09:10.072424	1
3486	169	2025-05-01	\N	\N	present	\N	2025-05-08 19:09:10.162764	2025-05-08 19:09:10.162769	1
3488	180	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:10.341831	2025-05-08 19:09:10.341836	1
3489	181	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:10.432382	2025-05-08 19:09:10.432387	1
3490	179	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:10.521818	2025-05-08 19:09:10.521847	1
3491	178	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:10.611658	2025-05-08 19:09:10.611662	1
3492	183	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:10.70123	2025-05-08 19:09:10.701234	1
3493	182	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:10.790879	2025-05-08 19:09:10.790883	1
3494	175	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:10.901614	2025-05-08 19:09:10.901619	1
3495	173	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:10.990989	2025-05-08 19:09:10.990994	1
3496	172	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:11.087961	2025-05-08 19:09:11.087966	1
3498	171	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:11.275433	2025-05-08 19:09:11.275437	1
3499	174	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:11.370153	2025-05-08 19:09:11.370157	1
3500	177	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:11.459649	2025-05-08 19:09:11.459653	1
3501	169	2025-05-02	\N	\N	present	\N	2025-05-08 19:09:11.550913	2025-05-08 19:09:11.550917	1
3503	180	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:11.729884	2025-05-08 19:09:11.729889	1
3504	181	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:11.819369	2025-05-08 19:09:11.819374	1
3505	179	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:11.910924	2025-05-08 19:09:11.910929	1
3506	178	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:12.002717	2025-05-08 19:09:12.002721	1
3507	183	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:12.100208	2025-05-08 19:09:12.100212	1
3508	182	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:12.194303	2025-05-08 19:09:12.194307	1
3509	175	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:12.283684	2025-05-08 19:09:12.283688	1
3510	173	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:12.374907	2025-05-08 19:09:12.374912	1
3511	172	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:12.465237	2025-05-08 19:09:12.46524	1
3513	171	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:12.648096	2025-05-08 19:09:12.648101	1
3514	174	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:12.738563	2025-05-08 19:09:12.738567	1
3515	177	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:12.828786	2025-05-08 19:09:12.82879	1
3516	169	2025-05-03	\N	\N	present	\N	2025-05-08 19:09:12.918767	2025-05-08 19:09:12.918772	1
3518	180	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:13.100047	2025-05-08 19:09:13.100051	1
3519	181	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:13.194931	2025-05-08 19:09:13.194936	1
3520	179	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:13.28575	2025-05-08 19:09:13.285755	1
3521	178	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:13.376227	2025-05-08 19:09:13.376231	1
3522	183	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:13.466762	2025-05-08 19:09:13.466766	1
3523	182	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:13.558262	2025-05-08 19:09:13.558266	1
3524	175	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:13.648638	2025-05-08 19:09:13.648642	1
3525	173	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:13.738848	2025-05-08 19:09:13.738853	1
3526	172	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:13.838788	2025-05-08 19:09:13.838793	1
3528	171	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:14.022351	2025-05-08 19:09:14.022355	1
3529	174	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:14.111789	2025-05-08 19:09:14.111793	1
3530	177	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:14.201608	2025-05-08 19:09:14.201613	1
3531	169	2025-05-04	\N	\N	present	\N	2025-05-08 19:09:14.290963	2025-05-08 19:09:14.290967	1
3533	180	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:14.488332	2025-05-08 19:09:14.488336	1
3534	181	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:14.582617	2025-05-08 19:09:14.582622	1
3535	179	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:14.672378	2025-05-08 19:09:14.672382	1
3536	178	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:14.762731	2025-05-08 19:09:14.762736	1
3546	169	2025-05-05	\N	\N	present	\N	2025-05-08 19:09:15.666099	2025-05-08 19:09:15.666104	1
3548	180	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:15.846387	2025-05-08 19:09:15.846392	1
3549	181	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:15.93604	2025-05-08 19:09:15.936044	1
3550	179	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:16.035317	2025-05-08 19:09:16.035322	1
3551	178	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:16.125703	2025-05-08 19:09:16.125715	1
3552	183	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:16.21523	2025-05-08 19:09:16.215234	1
3553	182	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:16.307751	2025-05-08 19:09:16.307755	1
3554	175	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:16.397461	2025-05-08 19:09:16.397466	1
3555	173	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:16.488179	2025-05-08 19:09:16.488183	1
3556	172	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:16.578893	2025-05-08 19:09:16.578897	1
3558	171	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:16.773764	2025-05-08 19:09:16.773768	1
3559	174	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:16.863888	2025-05-08 19:09:16.863893	1
3560	177	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:16.953606	2025-05-08 19:09:16.95361	1
3561	169	2025-05-06	\N	\N	present	\N	2025-05-08 19:09:17.044495	2025-05-08 19:09:17.044499	1
3563	180	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:17.224152	2025-05-08 19:09:17.224156	1
3564	181	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:17.314936	2025-05-08 19:09:17.31494	1
3565	179	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:17.404765	2025-05-08 19:09:17.404769	1
3566	178	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:17.494827	2025-05-08 19:09:17.494831	1
3567	183	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:17.584366	2025-05-08 19:09:17.584371	1
3568	182	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:17.673883	2025-05-08 19:09:17.673888	1
3569	175	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:17.763379	2025-05-08 19:09:17.763384	1
3570	173	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:17.853355	2025-05-08 19:09:17.85336	1
3571	172	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:17.94526	2025-05-08 19:09:17.945264	1
3573	171	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:18.130477	2025-05-08 19:09:18.130482	1
3574	174	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:18.221683	2025-05-08 19:09:18.221687	1
3575	177	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:18.311124	2025-05-08 19:09:18.311128	1
3576	169	2025-05-07	\N	\N	present	\N	2025-05-08 19:09:18.404838	2025-05-08 19:09:18.404843	1
3578	180	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:18.584289	2025-05-08 19:09:18.584293	1
3579	181	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:18.701534	2025-05-08 19:09:18.701539	1
3580	179	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:18.800902	2025-05-08 19:09:18.800907	1
3581	178	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:18.890368	2025-05-08 19:09:18.890372	1
3582	183	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:18.979521	2025-05-08 19:09:18.979526	1
3583	182	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:19.07679	2025-05-08 19:09:19.076795	1
3584	175	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:19.176494	2025-05-08 19:09:19.176498	1
3585	173	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:19.265897	2025-05-08 19:09:19.265901	1
3586	172	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:19.355515	2025-05-08 19:09:19.35552	1
3588	171	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:19.534736	2025-05-08 19:09:19.53474	1
3589	174	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:19.624654	2025-05-08 19:09:19.624658	1
3590	177	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:19.713917	2025-05-08 19:09:19.713922	1
3591	169	2025-05-08	\N	\N	present	\N	2025-05-08 19:09:19.803007	2025-05-08 19:09:19.803011	1
3593	193	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:20.645899	2025-05-08 19:11:20.645904	1
3594	191	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:20.739124	2025-05-08 19:11:20.739129	1
3595	189	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:20.828913	2025-05-08 19:11:20.828918	1
3596	190	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:20.917838	2025-05-08 19:11:20.917843	1
3597	192	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:21.007591	2025-05-08 19:11:21.007596	1
3598	193	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:21.096994	2025-05-08 19:11:21.096999	1
3599	191	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:21.186616	2025-05-08 19:11:21.18662	1
3600	189	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:21.300117	2025-05-08 19:11:21.300121	1
3601	190	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:21.39657	2025-05-08 19:11:21.396574	1
3602	192	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:21.486885	2025-05-08 19:11:21.486889	1
3603	193	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:21.582424	2025-05-08 19:11:21.582428	1
3604	191	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:21.671386	2025-05-08 19:11:21.67139	1
3605	189	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:21.760573	2025-05-08 19:11:21.760578	1
3606	190	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:21.853554	2025-05-08 19:11:21.853558	1
3607	192	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:21.951221	2025-05-08 19:11:21.951226	1
3608	193	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:22.039868	2025-05-08 19:11:22.03988	1
3609	191	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:22.128965	2025-05-08 19:11:22.12897	1
3610	189	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:22.218604	2025-05-08 19:11:22.218609	1
3611	190	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:22.307809	2025-05-08 19:11:22.307815	1
3612	192	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:22.396534	2025-05-08 19:11:22.396538	1
3613	193	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:22.487151	2025-05-08 19:11:22.487155	1
3614	191	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:22.583734	2025-05-08 19:11:22.583738	1
3615	189	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:22.673218	2025-05-08 19:11:22.673223	1
3616	190	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:22.762103	2025-05-08 19:11:22.762107	1
3617	192	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:22.851412	2025-05-08 19:11:22.851416	1
3618	193	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:22.941341	2025-05-08 19:11:22.941345	1
3619	191	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:23.03059	2025-05-08 19:11:23.030594	1
3620	189	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:23.120161	2025-05-08 19:11:23.120165	1
3621	190	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:23.21119	2025-05-08 19:11:23.211194	1
3622	192	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:23.300188	2025-05-08 19:11:23.300192	1
3623	193	2025-05-07	\N	\N	present	\N	2025-05-08 19:11:23.389897	2025-05-08 19:11:23.389901	1
3624	191	2025-05-07	\N	\N	present	\N	2025-05-08 19:11:23.479231	2025-05-08 19:11:23.479235	1
3625	189	2025-05-07	\N	\N	present	\N	2025-05-08 19:11:23.569124	2025-05-08 19:11:23.569128	1
3626	190	2025-05-07	\N	\N	present	\N	2025-05-08 19:11:23.660696	2025-05-08 19:11:23.660701	1
3627	192	2025-05-07	\N	\N	present	\N	2025-05-08 19:11:23.751063	2025-05-08 19:11:23.751067	1
3628	193	2025-05-08	\N	\N	present	\N	2025-05-08 19:11:23.842168	2025-05-08 19:11:23.842172	1
3629	191	2025-05-08	\N	\N	present	\N	2025-05-08 19:11:23.944731	2025-05-08 19:11:23.944735	1
3630	189	2025-05-08	\N	\N	present	\N	2025-05-08 19:11:24.042216	2025-05-08 19:11:24.042221	1
3631	190	2025-05-08	\N	\N	present	\N	2025-05-08 19:11:24.14097	2025-05-08 19:11:24.140975	1
3632	192	2025-05-08	\N	\N	present	\N	2025-05-08 19:11:24.229911	2025-05-08 19:11:24.229915	1
3633	194	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:47.95299	2025-05-08 19:11:47.952994	1
3634	195	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:48.043944	2025-05-08 19:11:48.043948	1
3635	196	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:48.18829	2025-05-08 19:11:48.188294	1
3636	197	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:48.281881	2025-05-08 19:11:48.281886	1
3638	200	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:48.462596	2025-05-08 19:11:48.4626	1
3639	202	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:48.551303	2025-05-08 19:11:48.551308	1
3640	203	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:48.640813	2025-05-08 19:11:48.640817	1
3641	205	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:48.729715	2025-05-08 19:11:48.729719	1
3642	206	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:48.818651	2025-05-08 19:11:48.818655	1
3643	207	2025-05-01	\N	\N	present	\N	2025-05-08 19:11:48.914947	2025-05-08 19:11:48.914952	1
3654	194	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:49.959326	2025-05-08 19:11:49.95933	1
3655	195	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:50.048641	2025-05-08 19:11:50.048646	1
3656	196	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:50.137509	2025-05-08 19:11:50.137514	1
3657	197	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:50.226381	2025-05-08 19:11:50.226386	1
3659	200	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:50.40845	2025-05-08 19:11:50.408454	1
3660	202	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:50.501477	2025-05-08 19:11:50.501482	1
3661	203	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:50.600493	2025-05-08 19:11:50.600497	1
3662	205	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:50.699685	2025-05-08 19:11:50.69969	1
3663	206	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:50.837407	2025-05-08 19:11:50.837411	1
3664	207	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:50.929536	2025-05-08 19:11:50.929541	1
3665	208	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:51.019962	2025-05-08 19:11:51.019967	1
3666	209	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:51.111543	2025-05-08 19:11:51.111548	1
3667	210	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:51.205256	2025-05-08 19:11:51.20526	1
3668	198	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:51.297385	2025-05-08 19:11:51.29739	1
3669	201	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:51.387677	2025-05-08 19:11:51.387681	1
3670	204	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:51.47706	2025-05-08 19:11:51.477065	1
3672	212	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:51.655306	2025-05-08 19:11:51.65531	1
3673	214	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:51.74678	2025-05-08 19:11:51.746785	1
3674	211	2025-05-02	\N	\N	present	\N	2025-05-08 19:11:51.843332	2025-05-08 19:11:51.843336	1
3675	194	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:51.933032	2025-05-08 19:11:51.933037	1
3676	195	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:52.022536	2025-05-08 19:11:52.022542	1
3677	196	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:52.113036	2025-05-08 19:11:52.113041	1
3678	197	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:52.203633	2025-05-08 19:11:52.203638	1
3680	200	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:52.387123	2025-05-08 19:11:52.387127	1
3681	202	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:52.483218	2025-05-08 19:11:52.483223	1
3682	203	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:52.573779	2025-05-08 19:11:52.573783	1
3683	205	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:52.662743	2025-05-08 19:11:52.662747	1
3684	206	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:52.752252	2025-05-08 19:11:52.752257	1
3685	207	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:52.841579	2025-05-08 19:11:52.841583	1
3686	208	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:52.935614	2025-05-08 19:11:52.935618	1
3687	209	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:53.024917	2025-05-08 19:11:53.024921	1
3688	210	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:53.113775	2025-05-08 19:11:53.11378	1
3689	198	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:53.203015	2025-05-08 19:11:53.203019	1
3690	201	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:53.292314	2025-05-08 19:11:53.292319	1
3691	204	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:53.381908	2025-05-08 19:11:53.381913	1
3693	212	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:53.564408	2025-05-08 19:11:53.564412	1
3694	214	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:53.655367	2025-05-08 19:11:53.655371	1
3695	211	2025-05-03	\N	\N	present	\N	2025-05-08 19:11:53.744611	2025-05-08 19:11:53.744615	1
3696	194	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:53.834233	2025-05-08 19:11:53.834238	1
3697	195	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:53.927888	2025-05-08 19:11:53.927892	1
3698	196	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:54.017169	2025-05-08 19:11:54.017174	1
3699	197	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:54.115019	2025-05-08 19:11:54.115024	1
3701	200	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:54.304405	2025-05-08 19:11:54.304409	1
3702	202	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:54.39365	2025-05-08 19:11:54.393655	1
3703	203	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:54.482671	2025-05-08 19:11:54.482676	1
3704	205	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:54.572548	2025-05-08 19:11:54.572552	1
3705	206	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:54.661745	2025-05-08 19:11:54.661749	1
3706	207	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:54.752365	2025-05-08 19:11:54.75237	1
3707	208	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:54.841235	2025-05-08 19:11:54.84124	1
3708	209	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:54.931188	2025-05-08 19:11:54.931192	1
3709	210	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:55.020146	2025-05-08 19:11:55.020151	1
3710	198	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:55.109324	2025-05-08 19:11:55.109329	1
3711	201	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:55.198669	2025-05-08 19:11:55.198675	1
3712	204	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:55.289748	2025-05-08 19:11:55.289752	1
3714	212	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:55.478759	2025-05-08 19:11:55.478763	1
3715	214	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:55.572135	2025-05-08 19:11:55.572139	1
3716	211	2025-05-04	\N	\N	present	\N	2025-05-08 19:11:55.664987	2025-05-08 19:11:55.664996	1
3717	194	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:55.753996	2025-05-08 19:11:55.754001	1
3718	195	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:55.844426	2025-05-08 19:11:55.84443	1
3719	196	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:55.933585	2025-05-08 19:11:55.933589	1
3720	197	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:56.022772	2025-05-08 19:11:56.022777	1
3722	200	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:56.203825	2025-05-08 19:11:56.203829	1
3723	202	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:56.292787	2025-05-08 19:11:56.292791	1
3724	203	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:56.398841	2025-05-08 19:11:56.398845	1
3725	205	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:56.493052	2025-05-08 19:11:56.493057	1
3726	206	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:56.584643	2025-05-08 19:11:56.584647	1
3727	207	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:56.678107	2025-05-08 19:11:56.678111	1
3728	208	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:56.774707	2025-05-08 19:11:56.774712	1
3729	209	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:56.867105	2025-05-08 19:11:56.86711	1
3730	210	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:56.964198	2025-05-08 19:11:56.964203	1
3731	198	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:57.055706	2025-05-08 19:11:57.05571	1
3732	201	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:57.145598	2025-05-08 19:11:57.145603	1
3733	204	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:57.235266	2025-05-08 19:11:57.235271	1
3735	212	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:57.41374	2025-05-08 19:11:57.413745	1
3736	214	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:57.506045	2025-05-08 19:11:57.506051	1
3737	211	2025-05-05	\N	\N	present	\N	2025-05-08 19:11:57.602225	2025-05-08 19:11:57.60223	1
3738	194	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:57.691158	2025-05-08 19:11:57.691163	1
3739	195	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:57.781711	2025-05-08 19:11:57.781716	1
3740	196	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:57.870938	2025-05-08 19:11:57.870943	1
3741	197	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:57.960263	2025-05-08 19:11:57.960267	1
3743	200	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:58.140866	2025-05-08 19:11:58.140871	1
3744	202	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:58.230463	2025-05-08 19:11:58.230468	1
3745	203	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:58.319751	2025-05-08 19:11:58.319756	1
3746	205	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:58.409486	2025-05-08 19:11:58.409491	1
3747	206	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:58.507195	2025-05-08 19:11:58.5072	1
3748	207	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:58.595961	2025-05-08 19:11:58.595965	1
3749	208	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:58.685017	2025-05-08 19:11:58.685037	1
3750	209	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:58.774254	2025-05-08 19:11:58.774259	1
3756	212	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:59.329952	2025-05-08 19:11:59.32997	1
3757	214	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:59.424574	2025-05-08 19:11:59.424578	1
3758	211	2025-05-06	\N	\N	present	\N	2025-05-08 19:11:59.514017	2025-05-08 19:11:59.514021	1
3759	194	2025-05-07	\N	\N	present	\N	2025-05-08 19:11:59.606466	2025-05-08 19:11:59.606471	1
3760	195	2025-05-07	\N	\N	present	\N	2025-05-08 19:11:59.704155	2025-05-08 19:11:59.70416	1
3761	196	2025-05-07	\N	\N	present	\N	2025-05-08 19:11:59.793473	2025-05-08 19:11:59.793478	1
3762	197	2025-05-07	\N	\N	present	\N	2025-05-08 19:11:59.882747	2025-05-08 19:11:59.882752	1
3764	200	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.066605	2025-05-08 19:12:00.06661	1
3765	202	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.155164	2025-05-08 19:12:00.155169	1
3766	203	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.244385	2025-05-08 19:12:00.24439	1
3767	205	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.349792	2025-05-08 19:12:00.349797	1
3768	206	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.441137	2025-05-08 19:12:00.441142	1
3769	207	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.530175	2025-05-08 19:12:00.530179	1
3770	208	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.619745	2025-05-08 19:12:00.619749	1
3771	209	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.709497	2025-05-08 19:12:00.709502	1
3772	210	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.800032	2025-05-08 19:12:00.800036	1
3773	198	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.890732	2025-05-08 19:12:00.890736	1
3774	201	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:00.981175	2025-05-08 19:12:00.98118	1
3775	204	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:01.071222	2025-05-08 19:12:01.071226	1
3777	212	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:01.257432	2025-05-08 19:12:01.257437	1
3778	214	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:01.346872	2025-05-08 19:12:01.346877	1
3779	211	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:01.438102	2025-05-08 19:12:01.438107	1
3780	194	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:01.527221	2025-05-08 19:12:01.527226	1
3781	195	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:01.616793	2025-05-08 19:12:01.616798	1
3782	196	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:01.706218	2025-05-08 19:12:01.706223	1
3783	197	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:01.79784	2025-05-08 19:12:01.797845	1
3785	200	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:01.980298	2025-05-08 19:12:01.980302	1
3786	202	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.073735	2025-05-08 19:12:02.07374	1
3787	203	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.171833	2025-05-08 19:12:02.171837	1
3788	205	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.261293	2025-05-08 19:12:02.261297	1
3789	206	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.352038	2025-05-08 19:12:02.352043	1
3790	207	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.441239	2025-05-08 19:12:02.441244	1
3791	208	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.530418	2025-05-08 19:12:02.530422	1
3792	209	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.6194	2025-05-08 19:12:02.619404	1
3793	210	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.709205	2025-05-08 19:12:02.709209	1
3794	198	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.805561	2025-05-08 19:12:02.805565	1
3795	201	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.899261	2025-05-08 19:12:02.899266	1
3796	204	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:02.99357	2025-05-08 19:12:02.993575	1
3798	212	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:03.187295	2025-05-08 19:12:03.1873	1
3799	214	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:03.276405	2025-05-08 19:12:03.276409	1
3800	211	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:03.367205	2025-05-08 19:12:03.367209	1
3801	216	2025-05-01	\N	\N	present	\N	2025-05-08 19:12:27.990596	2025-05-08 19:12:27.990601	1
3802	217	2025-05-01	\N	\N	present	\N	2025-05-08 19:12:28.080959	2025-05-08 19:12:28.080964	1
3803	218	2025-05-01	\N	\N	present	\N	2025-05-08 19:12:28.182719	2025-05-08 19:12:28.182724	1
3804	219	2025-05-01	\N	\N	present	\N	2025-05-08 19:12:28.277213	2025-05-08 19:12:28.277218	1
3805	220	2025-05-01	\N	\N	present	\N	2025-05-08 19:12:28.369041	2025-05-08 19:12:28.369045	1
3806	221	2025-05-01	\N	\N	present	\N	2025-05-08 19:12:28.460157	2025-05-08 19:12:28.460161	1
3807	222	2025-05-01	\N	\N	present	\N	2025-05-08 19:12:28.549423	2025-05-08 19:12:28.549427	1
3808	216	2025-05-02	\N	\N	present	\N	2025-05-08 19:12:28.638516	2025-05-08 19:12:28.63852	1
3809	217	2025-05-02	\N	\N	present	\N	2025-05-08 19:12:28.732893	2025-05-08 19:12:28.732898	1
3810	218	2025-05-02	\N	\N	present	\N	2025-05-08 19:12:28.822184	2025-05-08 19:12:28.82219	1
3811	219	2025-05-02	\N	\N	present	\N	2025-05-08 19:12:28.911063	2025-05-08 19:12:28.911068	1
3812	220	2025-05-02	\N	\N	present	\N	2025-05-08 19:12:29.002364	2025-05-08 19:12:29.002368	1
3813	221	2025-05-02	\N	\N	present	\N	2025-05-08 19:12:29.102068	2025-05-08 19:12:29.102073	1
3814	222	2025-05-02	\N	\N	present	\N	2025-05-08 19:12:29.191718	2025-05-08 19:12:29.191722	1
3815	216	2025-05-03	\N	\N	present	\N	2025-05-08 19:12:29.280693	2025-05-08 19:12:29.280699	1
3816	217	2025-05-03	\N	\N	present	\N	2025-05-08 19:12:29.369712	2025-05-08 19:12:29.369717	1
3817	218	2025-05-03	\N	\N	present	\N	2025-05-08 19:12:29.482133	2025-05-08 19:12:29.482137	1
3818	219	2025-05-03	\N	\N	present	\N	2025-05-08 19:12:29.615065	2025-05-08 19:12:29.61507	1
3819	220	2025-05-03	\N	\N	present	\N	2025-05-08 19:12:29.704293	2025-05-08 19:12:29.704297	1
3820	221	2025-05-03	\N	\N	present	\N	2025-05-08 19:12:29.793157	2025-05-08 19:12:29.793161	1
3821	222	2025-05-03	\N	\N	present	\N	2025-05-08 19:12:29.882169	2025-05-08 19:12:29.882173	1
3822	216	2025-05-04	\N	\N	present	\N	2025-05-08 19:12:29.971966	2025-05-08 19:12:29.972006	1
3823	217	2025-05-04	\N	\N	present	\N	2025-05-08 19:12:30.061574	2025-05-08 19:12:30.061579	1
3824	218	2025-05-04	\N	\N	present	\N	2025-05-08 19:12:30.1503	2025-05-08 19:12:30.150304	1
3825	219	2025-05-04	\N	\N	present	\N	2025-05-08 19:12:30.239494	2025-05-08 19:12:30.239498	1
3826	220	2025-05-04	\N	\N	present	\N	2025-05-08 19:12:30.335521	2025-05-08 19:12:30.335526	1
3827	221	2025-05-04	\N	\N	present	\N	2025-05-08 19:12:30.426487	2025-05-08 19:12:30.426491	1
3828	222	2025-05-04	\N	\N	present	\N	2025-05-08 19:12:30.519628	2025-05-08 19:12:30.519633	1
3829	216	2025-05-05	\N	\N	present	\N	2025-05-08 19:12:30.608416	2025-05-08 19:12:30.60842	1
3830	217	2025-05-05	\N	\N	present	\N	2025-05-08 19:12:30.697485	2025-05-08 19:12:30.69749	1
3831	218	2025-05-05	\N	\N	present	\N	2025-05-08 19:12:30.792206	2025-05-08 19:12:30.792211	1
3832	219	2025-05-05	\N	\N	present	\N	2025-05-08 19:12:30.883936	2025-05-08 19:12:30.88394	1
3833	220	2025-05-05	\N	\N	present	\N	2025-05-08 19:12:30.973262	2025-05-08 19:12:30.973266	1
3834	221	2025-05-05	\N	\N	present	\N	2025-05-08 19:12:31.071159	2025-05-08 19:12:31.071163	1
3835	222	2025-05-05	\N	\N	present	\N	2025-05-08 19:12:31.162908	2025-05-08 19:12:31.162912	1
3836	216	2025-05-06	\N	\N	present	\N	2025-05-08 19:12:31.252231	2025-05-08 19:12:31.252235	1
3837	217	2025-05-06	\N	\N	present	\N	2025-05-08 19:12:31.342177	2025-05-08 19:12:31.342182	1
3838	218	2025-05-06	\N	\N	present	\N	2025-05-08 19:12:31.430551	2025-05-08 19:12:31.430555	1
3839	219	2025-05-06	\N	\N	present	\N	2025-05-08 19:12:31.525705	2025-05-08 19:12:31.525709	1
3840	220	2025-05-06	\N	\N	present	\N	2025-05-08 19:12:31.616408	2025-05-08 19:12:31.616412	1
3841	221	2025-05-06	\N	\N	present	\N	2025-05-08 19:12:31.714436	2025-05-08 19:12:31.71444	1
3842	222	2025-05-06	\N	\N	present	\N	2025-05-08 19:12:31.803119	2025-05-08 19:12:31.803123	1
3843	216	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:31.893462	2025-05-08 19:12:31.893466	1
3844	217	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:31.98563	2025-05-08 19:12:31.985634	1
3845	218	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:32.074421	2025-05-08 19:12:32.074425	1
3846	219	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:32.163315	2025-05-08 19:12:32.16332	1
3847	220	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:32.252352	2025-05-08 19:12:32.252356	1
3848	221	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:32.34364	2025-05-08 19:12:32.343644	1
3849	222	2025-05-07	\N	\N	present	\N	2025-05-08 19:12:32.452225	2025-05-08 19:12:32.452229	1
3850	216	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:32.547029	2025-05-08 19:12:32.547035	1
3851	217	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:32.646648	2025-05-08 19:12:32.646653	1
3852	218	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:32.747371	2025-05-08 19:12:32.747375	1
3853	219	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:32.845234	2025-05-08 19:12:32.845237	1
3854	220	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:32.934105	2025-05-08 19:12:32.93411	1
3855	221	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:33.02386	2025-05-08 19:12:33.023954	1
3856	222	2025-05-08	\N	\N	present	\N	2025-05-08 19:12:33.113095	2025-05-08 19:12:33.113099	1
3857	184	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:00.65817	2025-05-09 10:59:00.658175	1
3865	178	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:13.598519	2025-05-09 10:59:13.598524	1
3866	183	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:13.685772	2025-05-09 10:59:13.685776	1
3867	182	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:13.771906	2025-05-09 10:59:13.771911	1
3868	175	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:13.86111	2025-05-09 10:59:13.861115	1
3869	173	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:13.947572	2025-05-09 10:59:13.947578	1
3870	172	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:14.038039	2025-05-09 10:59:14.038044	1
3872	171	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:14.210847	2025-05-09 10:59:14.210852	1
3873	174	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:14.297763	2025-05-09 10:59:14.297768	1
3874	177	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:14.384132	2025-05-09 10:59:14.384137	1
3875	169	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:14.484674	2025-05-09 10:59:14.484679	1
3877	193	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:29.788076	2025-05-09 10:59:29.788082	1
3878	191	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:29.875103	2025-05-09 10:59:29.875108	1
3879	189	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:29.961746	2025-05-09 10:59:29.961751	1
3880	190	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:30.047999	2025-05-09 10:59:30.048004	1
3881	192	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:30.134913	2025-05-09 10:59:30.134917	1
3882	194	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:43.211793	2025-05-09 10:59:43.211798	1
3883	195	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:43.298521	2025-05-09 10:59:43.298526	1
3884	196	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:43.385907	2025-05-09 10:59:43.385911	1
3885	197	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:43.472095	2025-05-09 10:59:43.472099	1
3887	200	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:43.645642	2025-05-09 10:59:43.645647	1
3888	202	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:43.732411	2025-05-09 10:59:43.732415	1
3889	203	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:43.820535	2025-05-09 10:59:43.82054	1
3890	205	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:43.913828	2025-05-09 10:59:43.913833	1
3891	206	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.001485	2025-05-09 10:59:44.00149	1
3892	207	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.089968	2025-05-09 10:59:44.089984	1
3893	208	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.177615	2025-05-09 10:59:44.17762	1
3894	209	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.276316	2025-05-09 10:59:44.276321	1
3895	210	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.366655	2025-05-09 10:59:44.36666	1
3896	198	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.45353	2025-05-09 10:59:44.453534	1
3897	201	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.541174	2025-05-09 10:59:44.541178	1
3898	204	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.627743	2025-05-09 10:59:44.627748	1
3900	212	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.800852	2025-05-09 10:59:44.800856	1
3901	214	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.887222	2025-05-09 10:59:44.887227	1
3902	211	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:44.973851	2025-05-09 10:59:44.973856	1
3903	216	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:59.678576	2025-05-09 10:59:59.678581	1
3904	217	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:59.76664	2025-05-09 10:59:59.766645	1
3905	218	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:59.853408	2025-05-09 10:59:59.853413	1
3906	219	2025-05-09	\N	\N	present	\N	2025-05-09 10:59:59.940021	2025-05-09 10:59:59.940026	1
3907	220	2025-05-09	\N	\N	present	\N	2025-05-09 11:00:00.026809	2025-05-09 11:00:00.026814	1
3908	221	2025-05-09	\N	\N	present	\N	2025-05-09 11:00:00.113863	2025-05-09 11:00:00.113868	1
3909	222	2025-05-09	\N	\N	present	\N	2025-05-09 11:00:00.201664	2025-05-09 11:00:00.20167	1
3910	184	2025-05-10	\N	\N	present	\N	2025-05-10 08:26:54.431615	2025-05-10 08:26:54.431621	1
3911	185	2025-05-10	\N	\N	present	\N	2025-05-10 08:26:54.529832	2025-05-10 08:26:54.529836	1
3912	186	2025-05-10	\N	\N	present	\N	2025-05-10 08:26:54.618698	2025-05-10 08:26:54.618703	1
3913	187	2025-05-10	\N	\N	present	\N	2025-05-10 08:26:54.707685	2025-05-10 08:26:54.70769	1
3914	188	2025-05-10	\N	\N	present	\N	2025-05-10 08:26:54.796543	2025-05-10 08:26:54.796548	1
3915	180	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:11.048316	2025-05-10 08:27:11.04832	1
3916	181	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:11.137878	2025-05-10 08:27:11.137883	1
3917	179	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:11.226387	2025-05-10 08:27:11.226392	1
3918	178	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:11.315027	2025-05-10 08:27:11.315032	1
3919	183	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:11.406393	2025-05-10 08:27:11.406398	1
3920	182	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:11.500757	2025-05-10 08:27:11.500761	1
3921	175	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:11.589547	2025-05-10 08:27:11.589552	1
3922	173	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:11.682245	2025-05-10 08:27:11.682249	1
3923	172	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:11.770822	2025-05-10 08:27:11.770826	1
3925	171	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:11.947929	2025-05-10 08:27:11.947934	1
3926	174	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:12.041454	2025-05-10 08:27:12.041469	1
3927	177	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:12.143312	2025-05-10 08:27:12.143317	1
3928	169	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:12.232305	2025-05-10 08:27:12.23231	1
3930	193	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:29.515116	2025-05-10 08:27:29.515123	1
3931	191	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:29.605959	2025-05-10 08:27:29.605964	1
3932	189	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:29.695203	2025-05-10 08:27:29.695208	1
3933	190	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:29.784177	2025-05-10 08:27:29.784182	1
3934	192	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:29.872871	2025-05-10 08:27:29.872875	1
3935	194	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:43.039202	2025-05-10 08:27:43.039207	1
3936	195	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:43.12879	2025-05-10 08:27:43.128795	1
3937	196	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:43.225669	2025-05-10 08:27:43.225674	1
3938	197	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:43.315298	2025-05-10 08:27:43.315303	1
3940	200	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:43.498325	2025-05-10 08:27:43.49833	1
3941	202	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:43.588373	2025-05-10 08:27:43.588378	1
3942	203	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:43.676604	2025-05-10 08:27:43.676609	1
3943	205	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:43.767301	2025-05-10 08:27:43.767306	1
3944	206	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:43.855761	2025-05-10 08:27:43.855765	1
3945	207	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:43.945207	2025-05-10 08:27:43.945212	1
3946	208	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:44.033476	2025-05-10 08:27:44.033489	1
3947	209	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:44.122694	2025-05-10 08:27:44.122699	1
3948	210	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:44.21922	2025-05-10 08:27:44.219225	1
3949	198	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:44.308448	2025-05-10 08:27:44.308453	1
3950	201	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:44.397574	2025-05-10 08:27:44.39758	1
3951	204	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:44.487089	2025-05-10 08:27:44.487094	1
3953	212	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:44.665293	2025-05-10 08:27:44.665297	1
3954	214	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:44.762315	2025-05-10 08:27:44.76232	1
3955	211	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:44.862332	2025-05-10 08:27:44.862336	1
3956	216	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:59.347425	2025-05-10 08:27:59.347431	1
3957	217	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:59.436706	2025-05-10 08:27:59.436712	1
3958	218	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:59.525507	2025-05-10 08:27:59.525512	1
3959	219	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:59.615125	2025-05-10 08:27:59.615131	1
3960	220	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:59.704366	2025-05-10 08:27:59.704373	1
3961	221	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:59.793389	2025-05-10 08:27:59.793394	1
3962	222	2025-05-10	\N	\N	present	\N	2025-05-10 08:27:59.882085	2025-05-10 08:27:59.88209	1
3963	184	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:20.63613	2025-05-12 11:52:20.636135	1
3964	185	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:20.742142	2025-05-12 11:52:20.742147	1
3970	186	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:21.317923	2025-05-12 11:52:21.317928	1
3971	187	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:21.404978	2025-05-12 11:52:21.404983	1
3972	188	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:21.492051	2025-05-12 11:52:21.492055	1
3973	180	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:50.715158	2025-05-12 11:52:50.715162	1
3974	181	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:50.812249	2025-05-12 11:52:50.812254	1
3975	179	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:50.901545	2025-05-12 11:52:50.90155	1
3976	178	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:50.996872	2025-05-12 11:52:50.996877	1
3977	183	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:51.085468	2025-05-12 11:52:51.085473	1
3978	182	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:51.175333	2025-05-12 11:52:51.175337	1
3979	175	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:51.26291	2025-05-12 11:52:51.262915	1
3980	173	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:51.349287	2025-05-12 11:52:51.349292	1
3981	172	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:51.436228	2025-05-12 11:52:51.436232	1
3983	171	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:51.610786	2025-05-12 11:52:51.610791	1
3984	174	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:51.697614	2025-05-12 11:52:51.697619	1
3985	177	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:51.784251	2025-05-12 11:52:51.784256	1
3986	169	2025-05-11	\N	\N	present	\N	2025-05-12 11:52:51.870469	2025-05-12 11:52:51.870474	1
3988	180	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:52.043085	2025-05-12 11:52:52.04309	1
3989	181	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:52.130519	2025-05-12 11:52:52.130524	1
3990	179	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:52.219787	2025-05-12 11:52:52.219792	1
3991	178	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:52.3073	2025-05-12 11:52:52.307305	1
3992	183	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:52.393704	2025-05-12 11:52:52.393709	1
3993	182	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:52.485297	2025-05-12 11:52:52.485302	1
3994	175	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:52.572249	2025-05-12 11:52:52.572254	1
3995	173	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:52.658346	2025-05-12 11:52:52.658351	1
3996	172	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:52.745771	2025-05-12 11:52:52.745776	1
3998	171	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:52.931316	2025-05-12 11:52:52.93132	1
3999	174	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:53.019677	2025-05-12 11:52:53.019682	1
4000	177	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:53.109403	2025-05-12 11:52:53.109408	1
4001	169	2025-05-12	\N	\N	present	\N	2025-05-12 11:52:53.195657	2025-05-12 11:52:53.195662	1
4003	193	2025-05-11	\N	\N	present	\N	2025-05-12 11:53:29.825694	2025-05-12 11:53:29.825699	1
4004	191	2025-05-11	\N	\N	present	\N	2025-05-12 11:53:29.919742	2025-05-12 11:53:29.919746	1
4005	189	2025-05-11	\N	\N	present	\N	2025-05-12 11:53:30.027923	2025-05-12 11:53:30.027928	1
4006	190	2025-05-11	\N	\N	present	\N	2025-05-12 11:53:30.131948	2025-05-12 11:53:30.131952	1
4007	192	2025-05-11	\N	\N	present	\N	2025-05-12 11:53:30.221431	2025-05-12 11:53:30.221436	1
4008	193	2025-05-12	\N	\N	present	\N	2025-05-12 11:53:30.313716	2025-05-12 11:53:30.31372	1
4009	191	2025-05-12	\N	\N	present	\N	2025-05-12 11:53:30.408894	2025-05-12 11:53:30.408899	1
4010	189	2025-05-12	\N	\N	present	\N	2025-05-12 11:53:30.494885	2025-05-12 11:53:30.49489	1
4011	190	2025-05-12	\N	\N	present	\N	2025-05-12 11:53:30.587035	2025-05-12 11:53:30.587039	1
4012	192	2025-05-12	\N	\N	present	\N	2025-05-12 11:53:30.675398	2025-05-12 11:53:30.675403	1
4013	194	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:57.396522	2025-05-12 11:54:57.396527	1
4014	195	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:57.48625	2025-05-12 11:54:57.486254	1
4015	196	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:57.585556	2025-05-12 11:54:57.585561	1
4016	197	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:57.675314	2025-05-12 11:54:57.675319	1
4018	200	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:57.852902	2025-05-12 11:54:57.852907	1
4019	202	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:57.944655	2025-05-12 11:54:57.94466	1
4020	203	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:58.0342	2025-05-12 11:54:58.034205	1
4021	205	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:58.136133	2025-05-12 11:54:58.136138	1
4022	206	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:58.231312	2025-05-12 11:54:58.231316	1
4023	207	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:58.327102	2025-05-12 11:54:58.327107	1
4024	208	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:58.418199	2025-05-12 11:54:58.41821	1
4025	209	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:58.508006	2025-05-12 11:54:58.50801	1
4026	210	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:58.605727	2025-05-12 11:54:58.605732	1
4027	198	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:58.705199	2025-05-12 11:54:58.705205	1
4028	201	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:58.80023	2025-05-12 11:54:58.800235	1
4029	204	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:58.900953	2025-05-12 11:54:58.900957	1
4031	212	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:59.078879	2025-05-12 11:54:59.078884	1
4032	214	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:59.167584	2025-05-12 11:54:59.167589	1
4033	211	2025-05-11	\N	\N	present	\N	2025-05-12 11:54:59.256955	2025-05-12 11:54:59.25696	1
4034	194	2025-05-12	\N	\N	present	\N	2025-05-12 11:54:59.346706	2025-05-12 11:54:59.346711	1
4035	195	2025-05-12	\N	\N	present	\N	2025-05-12 11:54:59.43607	2025-05-12 11:54:59.436075	1
4036	196	2025-05-12	\N	\N	present	\N	2025-05-12 11:54:59.525978	2025-05-12 11:54:59.525982	1
4037	197	2025-05-12	\N	\N	present	\N	2025-05-12 11:54:59.61501	2025-05-12 11:54:59.615015	1
4039	200	2025-05-12	\N	\N	present	\N	2025-05-12 11:54:59.795468	2025-05-12 11:54:59.795472	1
4040	202	2025-05-12	\N	\N	present	\N	2025-05-12 11:54:59.885573	2025-05-12 11:54:59.885577	1
4041	203	2025-05-12	\N	\N	present	\N	2025-05-12 11:54:59.974661	2025-05-12 11:54:59.974666	1
4042	205	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:00.063825	2025-05-12 11:55:00.06383	1
4043	206	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:00.15618	2025-05-12 11:55:00.156185	1
4044	207	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:00.245595	2025-05-12 11:55:00.2456	1
4045	208	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:00.334881	2025-05-12 11:55:00.334885	1
4046	209	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:00.425115	2025-05-12 11:55:00.42512	1
4047	210	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:00.514072	2025-05-12 11:55:00.514077	1
4048	198	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:00.603097	2025-05-12 11:55:00.603102	1
4049	201	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:00.693728	2025-05-12 11:55:00.693732	1
4050	204	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:00.785147	2025-05-12 11:55:00.785152	1
4052	212	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:00.964901	2025-05-12 11:55:00.964906	1
4053	214	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:01.057922	2025-05-12 11:55:01.057926	1
4054	211	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:01.147257	2025-05-12 11:55:01.147262	1
4055	216	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:18.10637	2025-05-12 11:55:18.106375	1
4056	217	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:18.196313	2025-05-12 11:55:18.196318	1
4057	218	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:18.285933	2025-05-12 11:55:18.285937	1
4058	219	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:18.377425	2025-05-12 11:55:18.37743	1
4059	220	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:18.46625	2025-05-12 11:55:18.466255	1
4060	221	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:18.555423	2025-05-12 11:55:18.555428	1
4061	222	2025-05-12	\N	\N	present	\N	2025-05-12 11:55:18.645488	2025-05-12 11:55:18.645493	1
4062	225	2025-05-12	\N	\N	present		2025-05-12 12:21:48.768893	2025-05-12 12:21:48.768897	1
4063	225	2025-05-01	\N	\N	present	\N	2025-05-12 13:25:30.678715	2025-05-12 13:25:30.678719	1
4064	225	2025-05-02	\N	\N	present	\N	2025-05-12 13:25:31.899408	2025-05-12 13:25:31.899412	1
4065	225	2025-05-03	\N	\N	present	\N	2025-05-12 13:25:32.874635	2025-05-12 13:25:32.874639	1
4066	225	2025-05-04	\N	\N	present	\N	2025-05-12 13:25:33.865178	2025-05-12 13:25:33.865182	1
4067	225	2025-05-05	\N	\N	present	\N	2025-05-12 13:25:34.85404	2025-05-12 13:25:34.854045	1
4068	225	2025-05-06	\N	\N	present	\N	2025-05-12 13:25:35.888258	2025-05-12 13:25:35.888262	1
4069	225	2025-05-07	\N	\N	present	\N	2025-05-12 13:25:36.945212	2025-05-12 13:25:36.945216	1
4070	225	2025-05-08	\N	\N	present	\N	2025-05-12 13:25:37.941499	2025-05-12 13:25:37.941504	1
4071	225	2025-05-09	\N	\N	present	\N	2025-05-12 13:25:38.984713	2025-05-12 13:25:38.984717	1
4072	225	2025-05-10	\N	\N	present	\N	2025-05-12 13:25:40.169114	2025-05-12 13:25:40.169123	1
4073	225	2025-05-11	\N	\N	present	\N	2025-05-12 13:25:41.282898	2025-05-12 13:25:41.282907	1
4159	204	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:43.136802	2025-05-13 21:36:43.136807	1
4160	212	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:43.227714	2025-05-13 21:36:43.227717	1
4161	214	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:43.322774	2025-05-13 21:36:43.322778	1
4162	211	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:43.411616	2025-05-13 21:36:43.41162	1
4163	225	2025-05-13	\N	\N	present	\N	2025-05-13 21:36:43.501427	2025-05-13 21:36:43.501431	1
4164	223	2025-05-01	\N	\N	present	\N	2025-05-13 21:52:09.537304	2025-05-13 21:52:09.537307	1
4165	224	2025-05-01	\N	\N	present	\N	2025-05-13 21:52:09.654709	2025-05-13 21:52:09.654713	1
4166	223	2025-05-02	\N	\N	present	\N	2025-05-13 21:52:09.74014	2025-05-13 21:52:09.740144	1
4167	224	2025-05-02	\N	\N	present	\N	2025-05-13 21:52:09.889923	2025-05-13 21:52:09.889926	1
4168	223	2025-05-03	\N	\N	present	\N	2025-05-13 21:52:09.974583	2025-05-13 21:52:09.974587	1
4169	224	2025-05-03	\N	\N	present	\N	2025-05-13 21:52:10.06482	2025-05-13 21:52:10.064824	1
4170	223	2025-05-04	\N	\N	present	\N	2025-05-13 21:52:10.159781	2025-05-13 21:52:10.159786	1
4171	224	2025-05-04	\N	\N	present	\N	2025-05-13 21:52:10.244624	2025-05-13 21:52:10.244628	1
4172	223	2025-05-05	\N	\N	present	\N	2025-05-13 21:52:10.324192	2025-05-13 21:52:10.324196	1
4173	224	2025-05-05	\N	\N	present	\N	2025-05-13 21:52:10.40814	2025-05-13 21:52:10.408144	1
4174	223	2025-05-06	\N	\N	present	\N	2025-05-13 21:52:10.49722	2025-05-13 21:52:10.497225	1
4175	224	2025-05-06	\N	\N	present	\N	2025-05-13 21:52:10.583708	2025-05-13 21:52:10.583712	1
4176	223	2025-05-07	\N	\N	present	\N	2025-05-13 21:52:10.679654	2025-05-13 21:52:10.679658	1
4177	224	2025-05-07	\N	\N	present	\N	2025-05-13 21:52:10.763347	2025-05-13 21:52:10.763369	1
4178	223	2025-05-08	\N	\N	present	\N	2025-05-13 21:52:10.848184	2025-05-13 21:52:10.848188	1
4179	224	2025-05-08	\N	\N	present	\N	2025-05-13 21:52:10.940079	2025-05-13 21:52:10.940084	1
4180	223	2025-05-09	\N	\N	present	\N	2025-05-13 21:52:11.023556	2025-05-13 21:52:11.023561	1
4181	224	2025-05-09	\N	\N	present	\N	2025-05-13 21:52:11.116111	2025-05-13 21:52:11.116115	1
4182	223	2025-05-10	\N	\N	present	\N	2025-05-13 21:52:11.203207	2025-05-13 21:52:11.203211	1
4184	223	2025-05-11	\N	\N	present	\N	2025-05-13 21:52:11.37529	2025-05-13 21:52:11.375295	1
4185	224	2025-05-11	\N	\N	present	\N	2025-05-13 21:52:11.461603	2025-05-13 21:52:11.461607	1
4186	223	2025-05-12	\N	\N	present	\N	2025-05-13 21:52:11.546412	2025-05-13 21:52:11.546416	1
4187	224	2025-05-12	\N	\N	present	\N	2025-05-13 21:52:11.634573	2025-05-13 21:52:11.634577	1
4188	223	2025-05-13	\N	\N	present	\N	2025-05-13 21:52:11.72543	2025-05-13 21:52:11.725443	1
4189	224	2025-05-13	\N	\N	present	\N	2025-05-13 21:52:11.816115	2025-05-13 21:52:11.816117	1
4190	216	2025-05-13	\N	\N	present	\N	2025-05-13 22:03:52.626322	2025-05-13 22:03:52.626326	1
4191	217	2025-05-13	\N	\N	present	\N	2025-05-13 22:03:52.73605	2025-05-13 22:03:52.736054	1
4192	218	2025-05-13	\N	\N	present	\N	2025-05-13 22:03:52.833016	2025-05-13 22:03:52.83302	1
4193	219	2025-05-13	\N	\N	present	\N	2025-05-13 22:03:52.92669	2025-05-13 22:03:52.926693	1
4194	220	2025-05-13	\N	\N	present	\N	2025-05-13 22:03:53.029269	2025-05-13 22:03:53.029272	1
4195	221	2025-05-13	\N	\N	present	\N	2025-05-13 22:03:53.13006	2025-05-13 22:03:53.130064	1
4196	222	2025-05-13	\N	\N	present	\N	2025-05-13 22:03:53.232123	2025-05-13 22:03:53.232127	1
4197	226	2025-05-01	\N	\N	present	\N	2025-05-13 22:15:52.92544	2025-05-13 22:15:52.925443	1
4198	226	2025-05-02	\N	\N	present	\N	2025-05-13 22:15:53.670812	2025-05-13 22:15:53.670816	1
4199	226	2025-05-03	\N	\N	present	\N	2025-05-13 22:15:54.411823	2025-05-13 22:15:54.411827	1
4200	226	2025-05-04	\N	\N	present	\N	2025-05-13 22:15:55.147154	2025-05-13 22:15:55.147158	1
4201	226	2025-05-05	\N	\N	present	\N	2025-05-13 22:15:55.88689	2025-05-13 22:15:55.886894	1
4202	226	2025-05-06	\N	\N	present	\N	2025-05-13 22:15:56.612089	2025-05-13 22:15:56.612093	1
4203	226	2025-05-07	\N	\N	present	\N	2025-05-13 22:15:57.370591	2025-05-13 22:15:57.370595	1
4204	226	2025-05-08	\N	\N	present	\N	2025-05-13 22:15:58.109765	2025-05-13 22:15:58.109769	1
4205	226	2025-05-09	\N	\N	present	\N	2025-05-13 22:15:58.832154	2025-05-13 22:15:58.832158	1
4206	226	2025-05-10	\N	\N	present	\N	2025-05-13 22:15:59.590502	2025-05-13 22:15:59.590505	1
4207	226	2025-05-11	\N	\N	present	\N	2025-05-13 22:16:00.406821	2025-05-13 22:16:00.406824	1
4208	226	2025-05-12	\N	\N	present	\N	2025-05-13 22:16:01.169333	2025-05-13 22:16:01.169337	1
4276	224	2025-05-14	\N	\N	present	\N	2025-05-14 11:11:07.934636	2025-05-14 11:11:07.934643	1
4277	184	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:51.628141	2025-05-16 13:26:51.628146	1
4278	185	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:51.74332	2025-05-16 13:26:51.743327	1
4210	184	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:28.828443	2025-05-14 11:01:28.828448	1
4211	185	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:28.933447	2025-05-14 11:01:28.933452	1
4212	186	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:29.027394	2025-05-14 11:01:29.0274	1
4213	187	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:29.121269	2025-05-14 11:01:29.121274	1
4214	188	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:29.218004	2025-05-14 11:01:29.218006	1
4215	227	2025-05-01	\N	\N	present	\N	2025-05-14 11:01:30.372446	2025-05-14 11:01:30.372456	1
4216	227	2025-05-02	\N	\N	present	\N	2025-05-14 11:01:31.176267	2025-05-14 11:01:31.176272	1
4217	227	2025-05-03	\N	\N	present	\N	2025-05-14 11:01:32.010664	2025-05-14 11:01:32.010668	1
4218	227	2025-05-04	\N	\N	present	\N	2025-05-14 11:01:32.786822	2025-05-14 11:01:32.786826	1
4219	227	2025-05-05	\N	\N	present	\N	2025-05-14 11:01:33.569273	2025-05-14 11:01:33.569278	1
4220	227	2025-05-06	\N	\N	present	\N	2025-05-14 11:01:34.387037	2025-05-14 11:01:34.387042	1
4221	227	2025-05-07	\N	\N	present	\N	2025-05-14 11:01:35.186235	2025-05-14 11:01:35.18624	1
4222	227	2025-05-08	\N	\N	present	\N	2025-05-14 11:01:35.993475	2025-05-14 11:01:35.993479	1
4223	227	2025-05-09	\N	\N	present	\N	2025-05-14 11:01:36.818187	2025-05-14 11:01:36.818194	1
4224	227	2025-05-10	\N	\N	present	\N	2025-05-14 11:01:37.596537	2025-05-14 11:01:37.596541	1
4225	227	2025-05-11	\N	\N	present	\N	2025-05-14 11:01:38.381334	2025-05-14 11:01:38.381338	1
4226	227	2025-05-12	\N	\N	present	\N	2025-05-14 11:01:39.164829	2025-05-14 11:01:39.164834	1
4209	226	2025-05-13	\N	\N	present		2025-05-13 22:16:01.906073	2025-05-14 11:01:39.887847	1
4227	227	2025-05-13	\N	\N	present	\N	2025-05-14 11:01:39.991782	2025-05-14 11:01:39.991787	1
4228	180	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:40.086412	2025-05-14 11:01:40.086417	1
4229	181	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:40.184732	2025-05-14 11:01:40.184737	1
4230	179	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:40.289933	2025-05-14 11:01:40.289937	1
4231	178	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:40.386261	2025-05-14 11:01:40.386265	1
4232	183	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:40.488121	2025-05-14 11:01:40.488126	1
4233	182	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:40.579014	2025-05-14 11:01:40.579019	1
4234	175	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:40.694506	2025-05-14 11:01:40.694511	1
4235	173	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:40.791129	2025-05-14 11:01:40.791134	1
4236	172	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:40.885539	2025-05-14 11:01:40.885544	1
4237	171	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:40.986234	2025-05-14 11:01:40.986239	1
4238	174	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:41.088581	2025-05-14 11:01:41.088586	1
4239	177	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:41.189096	2025-05-14 11:01:41.189101	1
4240	169	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:41.293598	2025-05-14 11:01:41.293603	1
4242	227	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:41.501471	2025-05-14 11:01:41.501474	1
4243	193	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:45.20709	2025-05-14 11:01:45.207095	1
4244	191	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:45.300824	2025-05-14 11:01:45.300829	1
4245	189	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:45.401199	2025-05-14 11:01:45.401204	1
4246	190	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:45.534052	2025-05-14 11:01:45.534065	1
4247	192	2025-05-14	\N	\N	present	\N	2025-05-14 11:01:45.631638	2025-05-14 11:01:45.631641	1
4248	194	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:11.867024	2025-05-14 11:03:11.867029	1
4249	195	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:11.957506	2025-05-14 11:03:11.957511	1
4250	196	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:12.056698	2025-05-14 11:03:12.056704	1
4251	197	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:12.148641	2025-05-14 11:03:12.148647	1
4252	200	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:12.235757	2025-05-14 11:03:12.235762	1
4253	202	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:12.321615	2025-05-14 11:03:12.321619	1
4254	203	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:12.408237	2025-05-14 11:03:12.408242	1
4255	205	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:12.494979	2025-05-14 11:03:12.494984	1
4256	206	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:12.58198	2025-05-14 11:03:12.581985	1
4257	207	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:12.667592	2025-05-14 11:03:12.667597	1
4258	208	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:12.753343	2025-05-14 11:03:12.753348	1
4259	209	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:12.841602	2025-05-14 11:03:12.841609	1
4260	210	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:13.00707	2025-05-14 11:03:13.007075	1
4261	198	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:13.093677	2025-05-14 11:03:13.093682	1
4262	201	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:13.179424	2025-05-14 11:03:13.179429	1
4263	204	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:13.266909	2025-05-14 11:03:13.266913	1
4264	212	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:13.353659	2025-05-14 11:03:13.353664	1
4265	214	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:13.439377	2025-05-14 11:03:13.439382	1
4266	211	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:13.530605	2025-05-14 11:03:13.53061	1
4267	225	2025-05-14	\N	\N	present	\N	2025-05-14 11:03:13.61781	2025-05-14 11:03:13.617814	1
4268	216	2025-05-14	\N	\N	present	\N	2025-05-14 11:08:27.848407	2025-05-14 11:08:27.848412	1
4269	217	2025-05-14	\N	\N	present	\N	2025-05-14 11:08:27.942239	2025-05-14 11:08:27.942245	1
4270	218	2025-05-14	\N	\N	present	\N	2025-05-14 11:08:28.056995	2025-05-14 11:08:28.057	1
4271	219	2025-05-14	\N	\N	present	\N	2025-05-14 11:08:28.1532	2025-05-14 11:08:28.153206	1
4272	220	2025-05-14	\N	\N	present	\N	2025-05-14 11:08:28.249397	2025-05-14 11:08:28.249403	1
4273	221	2025-05-14	\N	\N	present	\N	2025-05-14 11:08:28.338608	2025-05-14 11:08:28.338613	1
4274	222	2025-05-14	\N	\N	present	\N	2025-05-14 11:08:28.434459	2025-05-14 11:08:28.434464	1
4275	223	2025-05-14	\N	\N	present	\N	2025-05-14 11:11:07.844544	2025-05-14 11:11:07.844549	1
4279	186	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:51.846226	2025-05-16 13:26:51.846231	1
4280	187	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:51.94948	2025-05-16 13:26:51.949485	1
4281	188	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:52.04716	2025-05-16 13:26:52.047162	1
4282	180	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:52.479032	2025-05-16 13:26:52.479037	1
4283	181	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:52.589896	2025-05-16 13:26:52.589901	1
4284	179	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:52.683631	2025-05-16 13:26:52.683636	1
4285	178	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:52.776609	2025-05-16 13:26:52.776655	1
4286	183	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:52.87669	2025-05-16 13:26:52.876695	1
4287	182	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:52.975184	2025-05-16 13:26:52.975189	1
4288	175	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:53.069425	2025-05-16 13:26:53.06943	1
4289	173	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:53.165097	2025-05-16 13:26:53.165102	1
4290	172	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:53.258026	2025-05-16 13:26:53.258031	1
4291	171	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:53.35178	2025-05-16 13:26:53.351786	1
4292	174	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:53.452957	2025-05-16 13:26:53.452962	1
4293	177	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:53.549782	2025-05-16 13:26:53.549787	1
4294	169	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:53.65089	2025-05-16 13:26:53.650896	1
4295	226	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:53.758544	2025-05-16 13:26:53.758549	1
4296	227	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:53.855773	2025-05-16 13:26:53.855775	1
4297	193	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:54.321307	2025-05-16 13:26:54.321312	1
4298	191	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:54.418699	2025-05-16 13:26:54.418704	1
4299	189	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:54.515816	2025-05-16 13:26:54.515836	1
4300	190	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:54.614715	2025-05-16 13:26:54.61472	1
4301	192	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:54.710348	2025-05-16 13:26:54.71035	1
4302	194	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:55.156925	2025-05-16 13:26:55.156932	1
4303	195	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:55.24985	2025-05-16 13:26:55.249856	1
4304	196	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:55.349437	2025-05-16 13:26:55.349443	1
4305	197	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:55.446072	2025-05-16 13:26:55.446077	1
4306	200	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:55.541456	2025-05-16 13:26:55.541461	1
4307	202	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:55.640485	2025-05-16 13:26:55.64049	1
4308	203	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:55.734807	2025-05-16 13:26:55.734812	1
4309	205	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:55.832439	2025-05-16 13:26:55.832445	1
4310	206	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:55.933499	2025-05-16 13:26:55.933504	1
4311	207	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:56.034079	2025-05-16 13:26:56.034084	1
4312	208	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:56.127186	2025-05-16 13:26:56.127191	1
4313	209	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:56.221461	2025-05-16 13:26:56.221466	1
4314	210	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:56.319535	2025-05-16 13:26:56.31954	1
4315	198	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:56.420745	2025-05-16 13:26:56.42075	1
4316	201	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:56.516378	2025-05-16 13:26:56.516384	1
4317	204	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:56.619575	2025-05-16 13:26:56.61958	1
4318	212	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:56.710921	2025-05-16 13:26:56.710926	1
4319	214	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:56.81443	2025-05-16 13:26:56.814435	1
4320	211	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:56.918471	2025-05-16 13:26:56.918476	1
4321	225	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:57.023488	2025-05-16 13:26:57.023489	1
4322	216	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:57.447108	2025-05-16 13:26:57.447113	1
4323	217	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:57.537765	2025-05-16 13:26:57.53777	1
4324	218	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:57.636145	2025-05-16 13:26:57.63615	1
4325	219	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:57.732495	2025-05-16 13:26:57.732499	1
4326	220	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:57.834314	2025-05-16 13:26:57.834319	1
4327	221	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:57.936627	2025-05-16 13:26:57.936632	1
4328	222	2025-05-16	\N	\N	present	\N	2025-05-16 13:26:58.038993	2025-05-16 13:26:58.038995	1
4329	184	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:55.158699	2025-05-16 13:27:55.158704	1
4330	185	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:55.251936	2025-05-16 13:27:55.25194	1
4331	186	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:55.349469	2025-05-16 13:27:55.349474	1
4332	187	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:55.446828	2025-05-16 13:27:55.446855	1
4333	188	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:55.542862	2025-05-16 13:27:55.542867	1
4334	180	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:56.229051	2025-05-16 13:27:56.229057	1
4335	181	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:56.321101	2025-05-16 13:27:56.321106	1
4336	179	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:56.420495	2025-05-16 13:27:56.420499	1
4337	178	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:56.515728	2025-05-16 13:27:56.515734	1
4338	183	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:56.62237	2025-05-16 13:27:56.622374	1
4339	182	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:56.71875	2025-05-16 13:27:56.718756	1
4340	175	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:56.812261	2025-05-16 13:27:56.812265	1
4341	173	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:56.9059	2025-05-16 13:27:56.905906	1
4342	172	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:57.008473	2025-05-16 13:27:57.008478	1
4343	171	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:57.112131	2025-05-16 13:27:57.112136	1
4344	174	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:57.208961	2025-05-16 13:27:57.208965	1
4345	177	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:57.299393	2025-05-16 13:27:57.299397	1
4346	169	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:57.392536	2025-05-16 13:27:57.392541	1
4347	226	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:57.487861	2025-05-16 13:27:57.487866	1
4348	227	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:57.579735	2025-05-16 13:27:57.57974	1
4349	193	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:58.72381	2025-05-16 13:27:58.723815	1
4350	191	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:58.815449	2025-05-16 13:27:58.815454	1
4351	189	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:58.909355	2025-05-16 13:27:58.90936	1
4352	190	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:59.004762	2025-05-16 13:27:59.004767	1
4353	192	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:59.102704	2025-05-16 13:27:59.102709	1
4354	194	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:59.769032	2025-05-16 13:27:59.769037	1
4355	195	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:59.865476	2025-05-16 13:27:59.865481	1
4356	196	2025-05-15	\N	\N	present	\N	2025-05-16 13:27:59.955847	2025-05-16 13:27:59.955852	1
4357	197	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.048073	2025-05-16 13:28:00.048077	1
4358	200	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.139491	2025-05-16 13:28:00.139496	1
4359	202	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.231914	2025-05-16 13:28:00.231919	1
4360	203	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.322423	2025-05-16 13:28:00.322428	1
4361	205	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.414477	2025-05-16 13:28:00.414481	1
4362	206	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.508127	2025-05-16 13:28:00.508132	1
4363	207	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.600266	2025-05-16 13:28:00.600271	1
4364	208	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.698625	2025-05-16 13:28:00.698629	1
4365	209	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.796282	2025-05-16 13:28:00.796287	1
4366	210	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.89657	2025-05-16 13:28:00.896574	1
4367	198	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:00.992661	2025-05-16 13:28:00.992666	1
4368	201	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:01.09119	2025-05-16 13:28:01.091194	1
4369	204	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:01.182666	2025-05-16 13:28:01.182671	1
4370	212	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:01.27521	2025-05-16 13:28:01.275215	1
4371	214	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:01.372681	2025-05-16 13:28:01.372686	1
4372	211	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:01.464962	2025-05-16 13:28:01.464966	1
4373	225	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:01.557252	2025-05-16 13:28:01.557256	1
4374	216	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:02.943045	2025-05-16 13:28:02.943049	1
4375	217	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:03.04216	2025-05-16 13:28:03.042165	1
4376	218	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:03.14031	2025-05-16 13:28:03.140317	1
4377	219	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:03.233457	2025-05-16 13:28:03.233462	1
4378	220	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:03.330601	2025-05-16 13:28:03.330606	1
4379	221	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:03.422262	2025-05-16 13:28:03.422266	1
4380	222	2025-05-15	\N	\N	present	\N	2025-05-16 13:28:03.512461	2025-05-16 13:28:03.512466	1
4381	223	2025-05-15	\N	\N	present	\N	2025-05-16 13:29:13.034073	2025-05-16 13:29:13.034078	1
4382	224	2025-05-15	\N	\N	present	\N	2025-05-16 13:29:13.132647	2025-05-16 13:29:13.132652	1
4383	223	2025-05-16	\N	\N	present	\N	2025-05-16 13:29:13.243668	2025-05-16 13:29:13.243673	1
4384	224	2025-05-16	\N	\N	present	\N	2025-05-16 13:29:13.334454	2025-05-16 13:29:13.334455	1
4385	184	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:32.503506	2025-05-17 10:17:32.503511	1
4386	185	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:32.620369	2025-05-17 10:17:32.620375	1
4387	186	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:32.710657	2025-05-17 10:17:32.710662	1
4388	187	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:32.803966	2025-05-17 10:17:32.803985	1
4389	188	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:32.894339	2025-05-17 10:17:32.894342	1
4390	180	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:33.296011	2025-05-17 10:17:33.296017	1
4391	181	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:33.385597	2025-05-17 10:17:33.385602	1
4392	179	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:33.474331	2025-05-17 10:17:33.474336	1
4393	178	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:33.567301	2025-05-17 10:17:33.567306	1
4394	183	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:33.656099	2025-05-17 10:17:33.656104	1
4395	182	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:33.745221	2025-05-17 10:17:33.745226	1
4396	175	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:33.833753	2025-05-17 10:17:33.833763	1
4397	173	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:33.922673	2025-05-17 10:17:33.922679	1
4398	172	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:34.012803	2025-05-17 10:17:34.012808	1
4399	171	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:34.102492	2025-05-17 10:17:34.102497	1
4400	174	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:34.192447	2025-05-17 10:17:34.192451	1
4401	177	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:34.281461	2025-05-17 10:17:34.281466	1
4402	169	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:34.370402	2025-05-17 10:17:34.370407	1
4403	226	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:34.459698	2025-05-17 10:17:34.459703	1
4404	227	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:34.548348	2025-05-17 10:17:34.54835	1
4405	193	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:34.944405	2025-05-17 10:17:34.944409	1
4406	191	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:35.033086	2025-05-17 10:17:35.033091	1
4407	189	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:35.121904	2025-05-17 10:17:35.12191	1
4408	190	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:35.211773	2025-05-17 10:17:35.211777	1
4409	192	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:35.301057	2025-05-17 10:17:35.30106	1
4410	194	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:35.697304	2025-05-17 10:17:35.69731	1
4411	195	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:35.786278	2025-05-17 10:17:35.786284	1
4412	196	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:35.879643	2025-05-17 10:17:35.879648	1
4413	197	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:35.968568	2025-05-17 10:17:35.968573	1
4414	200	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.056921	2025-05-17 10:17:36.056926	1
4415	202	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.146112	2025-05-17 10:17:36.146117	1
4416	203	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.234908	2025-05-17 10:17:36.234913	1
4417	205	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.324076	2025-05-17 10:17:36.324081	1
4418	206	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.412742	2025-05-17 10:17:36.412747	1
4419	207	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.501729	2025-05-17 10:17:36.501735	1
4420	208	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.590349	2025-05-17 10:17:36.590354	1
4421	209	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.67882	2025-05-17 10:17:36.678825	1
4422	210	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.76801	2025-05-17 10:17:36.768015	1
4423	198	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.859075	2025-05-17 10:17:36.85908	1
4424	201	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:36.955229	2025-05-17 10:17:36.955234	1
4425	204	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:37.050725	2025-05-17 10:17:37.05073	1
4426	214	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:37.141121	2025-05-17 10:17:37.141125	1
4427	225	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:37.243618	2025-05-17 10:17:37.243621	1
4428	216	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:37.653392	2025-05-17 10:17:37.653397	1
4429	217	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:37.743116	2025-05-17 10:17:37.743121	1
4430	218	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:37.832114	2025-05-17 10:17:37.83212	1
4431	219	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:37.920825	2025-05-17 10:17:37.92083	1
4432	220	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:38.021184	2025-05-17 10:17:38.021189	1
4433	221	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:38.110919	2025-05-17 10:17:38.110924	1
4434	222	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:38.202265	2025-05-17 10:17:38.202267	1
4435	223	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:38.598304	2025-05-17 10:17:38.598309	1
4436	224	2025-05-17	\N	\N	present	\N	2025-05-17 10:17:38.686881	2025-05-17 10:17:38.686883	1
4437	184	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:53.388508	2025-05-18 10:23:53.388512	1
4438	185	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:53.488855	2025-05-18 10:23:53.48886	1
4439	186	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:53.578435	2025-05-18 10:23:53.57844	1
4440	187	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:53.670348	2025-05-18 10:23:53.670353	1
4441	188	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:53.759886	2025-05-18 10:23:53.759889	1
4442	180	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:54.168262	2025-05-18 10:23:54.168267	1
4443	181	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:54.263108	2025-05-18 10:23:54.263112	1
4444	179	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:54.351275	2025-05-18 10:23:54.351279	1
4445	178	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:54.439722	2025-05-18 10:23:54.439727	1
4446	183	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:54.530094	2025-05-18 10:23:54.530098	1
4447	182	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:54.620662	2025-05-18 10:23:54.620667	1
4448	175	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:54.71543	2025-05-18 10:23:54.715434	1
4449	173	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:54.804763	2025-05-18 10:23:54.804768	1
4450	172	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:54.902403	2025-05-18 10:23:54.902407	1
4451	171	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:55.003284	2025-05-18 10:23:55.003289	1
4452	174	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:55.093517	2025-05-18 10:23:55.093522	1
4453	177	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:55.188112	2025-05-18 10:23:55.188117	1
4454	169	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:55.280687	2025-05-18 10:23:55.280691	1
4455	226	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:55.372345	2025-05-18 10:23:55.372351	1
4456	227	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:55.461143	2025-05-18 10:23:55.461145	1
4457	193	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:55.864941	2025-05-18 10:23:55.864945	1
4458	191	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:55.962902	2025-05-18 10:23:55.962907	1
4459	189	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:56.05273	2025-05-18 10:23:56.052734	1
4460	190	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:56.147494	2025-05-18 10:23:56.147498	1
4461	192	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:56.239666	2025-05-18 10:23:56.239668	1
4462	194	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:56.659451	2025-05-18 10:23:56.659455	1
4463	195	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:56.749478	2025-05-18 10:23:56.749483	1
4464	196	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:56.839832	2025-05-18 10:23:56.839847	1
4465	197	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:56.92965	2025-05-18 10:23:56.929655	1
4466	200	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.022584	2025-05-18 10:23:57.022589	1
4467	202	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.115618	2025-05-18 10:23:57.115623	1
4468	203	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.204999	2025-05-18 10:23:57.205004	1
4469	205	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.293246	2025-05-18 10:23:57.293251	1
4470	206	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.383659	2025-05-18 10:23:57.383663	1
4471	207	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.471837	2025-05-18 10:23:57.471841	1
4472	208	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.562291	2025-05-18 10:23:57.562296	1
4473	209	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.650518	2025-05-18 10:23:57.650522	1
4474	210	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.73937	2025-05-18 10:23:57.739375	1
4475	198	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.827268	2025-05-18 10:23:57.827272	1
4476	201	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:57.918636	2025-05-18 10:23:57.91864	1
4477	204	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:58.008008	2025-05-18 10:23:58.008013	1
4478	214	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:58.096307	2025-05-18 10:23:58.096311	1
4479	225	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:58.184671	2025-05-18 10:23:58.184673	1
4480	216	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:58.577294	2025-05-18 10:23:58.577299	1
4481	217	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:58.666093	2025-05-18 10:23:58.666098	1
4482	218	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:58.755279	2025-05-18 10:23:58.755284	1
4483	219	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:58.843733	2025-05-18 10:23:58.843738	1
4484	220	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:58.937398	2025-05-18 10:23:58.937402	1
4485	221	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:59.026762	2025-05-18 10:23:59.026766	1
4486	222	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:59.118407	2025-05-18 10:23:59.118409	1
4487	223	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:59.522136	2025-05-18 10:23:59.522141	1
4488	224	2025-05-18	\N	\N	present	\N	2025-05-18 10:23:59.609857	2025-05-18 10:23:59.60986	1
4489	184	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:37.147235	2025-05-19 06:41:37.147241	1
4490	185	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:37.263673	2025-05-19 06:41:37.263679	1
4491	186	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:37.356906	2025-05-19 06:41:37.356911	1
4492	187	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:37.448948	2025-05-19 06:41:37.448953	1
4493	188	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:37.547883	2025-05-19 06:41:37.547886	1
4494	180	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:37.986818	2025-05-19 06:41:37.986823	1
4495	181	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:38.07786	2025-05-19 06:41:38.077865	1
4496	179	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:38.170886	2025-05-19 06:41:38.170891	1
4497	178	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:38.265793	2025-05-19 06:41:38.265798	1
4498	182	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:38.358779	2025-05-19 06:41:38.358784	1
4499	175	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:38.450706	2025-05-19 06:41:38.450711	1
4500	173	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:38.547442	2025-05-19 06:41:38.547446	1
4501	172	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:38.638913	2025-05-19 06:41:38.638918	1
4502	171	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:38.734531	2025-05-19 06:41:38.734537	1
4503	174	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:38.830746	2025-05-19 06:41:38.830751	1
4504	177	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:38.921432	2025-05-19 06:41:38.921437	1
4505	169	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:39.014693	2025-05-19 06:41:39.014698	1
4506	183	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:39.112922	2025-05-19 06:41:39.112926	1
4507	226	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:39.205338	2025-05-19 06:41:39.205343	1
4508	227	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:39.299866	2025-05-19 06:41:39.299867	1
4509	193	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:39.709285	2025-05-19 06:41:39.709291	1
4510	191	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:39.799506	2025-05-19 06:41:39.799511	1
4511	189	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:39.896759	2025-05-19 06:41:39.896765	1
4512	190	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:39.987308	2025-05-19 06:41:39.987313	1
4513	192	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:40.08292	2025-05-19 06:41:40.082922	1
4514	194	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:40.728291	2025-05-19 06:41:40.728296	1
4515	195	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:40.820239	2025-05-19 06:41:40.820243	1
4516	196	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:40.912384	2025-05-19 06:41:40.912389	1
4517	197	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.008454	2025-05-19 06:41:41.008459	1
4518	200	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.104082	2025-05-19 06:41:41.104087	1
4519	202	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.199279	2025-05-19 06:41:41.199284	1
4520	203	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.298568	2025-05-19 06:41:41.298572	1
4521	205	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.401692	2025-05-19 06:41:41.401698	1
4522	206	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.497319	2025-05-19 06:41:41.497324	1
4523	207	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.602762	2025-05-19 06:41:41.602767	1
4524	208	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.69534	2025-05-19 06:41:41.695345	1
4525	209	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.786814	2025-05-19 06:41:41.786819	1
4526	210	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.879308	2025-05-19 06:41:41.879313	1
4527	198	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:41.969514	2025-05-19 06:41:41.969519	1
4528	201	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:42.065879	2025-05-19 06:41:42.065883	1
4529	204	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:42.16604	2025-05-19 06:41:42.166045	1
4530	214	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:42.2613	2025-05-19 06:41:42.261305	1
4531	225	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:42.359858	2025-05-19 06:41:42.35986	1
4532	216	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:42.784757	2025-05-19 06:41:42.784762	1
4533	217	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:42.896176	2025-05-19 06:41:42.89618	1
4534	218	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:42.99187	2025-05-19 06:41:42.991875	1
4535	219	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:43.087283	2025-05-19 06:41:43.087288	1
4536	220	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:43.182633	2025-05-19 06:41:43.182638	1
4537	221	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:43.275464	2025-05-19 06:41:43.275469	1
4538	222	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:43.371471	2025-05-19 06:41:43.371473	1
4539	223	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:43.79973	2025-05-19 06:41:43.799735	1
4540	224	2025-05-19	\N	\N	present	\N	2025-05-19 06:41:43.895288	2025-05-19 06:41:43.89529	1
4541	184	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:33.226762	2025-05-20 12:39:33.226767	1
4542	185	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:33.336407	2025-05-20 12:39:33.336413	1
4543	186	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:33.436849	2025-05-20 12:39:33.436855	1
4544	187	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:33.533823	2025-05-20 12:39:33.533828	1
4545	188	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:33.629427	2025-05-20 12:39:33.629429	1
4546	180	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:34.077374	2025-05-20 12:39:34.07738	1
4547	181	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:34.178428	2025-05-20 12:39:34.178434	1
4548	179	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:34.27131	2025-05-20 12:39:34.271315	1
4549	178	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:34.371806	2025-05-20 12:39:34.371811	1
4550	182	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:34.479818	2025-05-20 12:39:34.479823	1
4551	175	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:34.576842	2025-05-20 12:39:34.576847	1
4552	173	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:34.68248	2025-05-20 12:39:34.682485	1
4553	172	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:34.790069	2025-05-20 12:39:34.790075	1
4554	171	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:34.889729	2025-05-20 12:39:34.889734	1
4555	174	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:34.989491	2025-05-20 12:39:34.989496	1
4556	177	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:35.099764	2025-05-20 12:39:35.099769	1
4557	169	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:35.19529	2025-05-20 12:39:35.195295	1
4558	183	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:35.298655	2025-05-20 12:39:35.29866	1
4559	226	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:35.392232	2025-05-20 12:39:35.392237	1
4560	227	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:35.492205	2025-05-20 12:39:35.492207	1
4561	193	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:35.931366	2025-05-20 12:39:35.931371	1
4562	191	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:36.027902	2025-05-20 12:39:36.027907	1
4563	189	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:36.137236	2025-05-20 12:39:36.137241	1
4564	190	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:36.234691	2025-05-20 12:39:36.234697	1
4565	192	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:36.331342	2025-05-20 12:39:36.331344	1
4566	194	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:36.77011	2025-05-20 12:39:36.770115	1
4567	195	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:36.867911	2025-05-20 12:39:36.867917	1
4568	196	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:36.964714	2025-05-20 12:39:36.964719	1
4569	197	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:37.063201	2025-05-20 12:39:37.063206	1
4570	200	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:37.160634	2025-05-20 12:39:37.16064	1
4571	202	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:37.272594	2025-05-20 12:39:37.272599	1
4572	203	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:37.372212	2025-05-20 12:39:37.372217	1
4573	205	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:37.471506	2025-05-20 12:39:37.471512	1
4574	206	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:37.565801	2025-05-20 12:39:37.565807	1
4575	207	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:37.662691	2025-05-20 12:39:37.662696	1
4576	208	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:37.768609	2025-05-20 12:39:37.768614	1
4577	209	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:37.87115	2025-05-20 12:39:37.871162	1
4578	210	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:37.968516	2025-05-20 12:39:37.968521	1
4579	198	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:38.082574	2025-05-20 12:39:38.082579	1
4580	201	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:38.186847	2025-05-20 12:39:38.186852	1
4581	204	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:38.287212	2025-05-20 12:39:38.287217	1
4582	214	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:38.437194	2025-05-20 12:39:38.4372	1
4583	225	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:38.533059	2025-05-20 12:39:38.533061	1
4584	216	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:38.97952	2025-05-20 12:39:38.979525	1
4585	217	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:39.079288	2025-05-20 12:39:39.079295	1
4586	218	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:39.173652	2025-05-20 12:39:39.173657	1
4587	219	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:39.267858	2025-05-20 12:39:39.267863	1
4588	220	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:39.375876	2025-05-20 12:39:39.375881	1
4589	221	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:39.483551	2025-05-20 12:39:39.483556	1
4590	222	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:39.589094	2025-05-20 12:39:39.589096	1
4591	223	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:40.027237	2025-05-20 12:39:40.027241	1
4592	224	2025-05-20	\N	\N	present	\N	2025-05-20 12:39:40.123241	2025-05-20 12:39:40.123243	1
4593	184	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:50.3424	2025-05-21 15:18:50.342406	1
4594	185	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:50.46356	2025-05-21 15:18:50.463565	1
4595	186	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:50.562124	2025-05-21 15:18:50.562129	1
4596	187	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:50.653696	2025-05-21 15:18:50.653701	1
4597	188	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:50.750652	2025-05-21 15:18:50.750655	1
4598	180	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:51.187489	2025-05-21 15:18:51.187494	1
4599	181	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:51.292653	2025-05-21 15:18:51.292658	1
4600	179	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:51.383363	2025-05-21 15:18:51.383368	1
4601	178	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:51.48929	2025-05-21 15:18:51.489304	1
4602	182	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:51.588504	2025-05-21 15:18:51.588509	1
4603	175	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:51.677771	2025-05-21 15:18:51.677775	1
4604	173	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:51.771035	2025-05-21 15:18:51.77104	1
4605	172	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:51.862664	2025-05-21 15:18:51.862669	1
4606	171	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:51.958976	2025-05-21 15:18:51.958981	1
4607	174	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:52.057791	2025-05-21 15:18:52.057796	1
4608	177	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:52.168826	2025-05-21 15:18:52.168831	1
4609	169	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:52.263206	2025-05-21 15:18:52.263211	1
4610	183	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:52.362198	2025-05-21 15:18:52.362203	1
4611	226	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:52.452924	2025-05-21 15:18:52.45293	1
4612	227	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:52.576959	2025-05-21 15:18:52.576962	1
4613	193	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:53.026198	2025-05-21 15:18:53.026203	1
4614	191	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:53.14538	2025-05-21 15:18:53.145385	1
4615	189	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:53.272548	2025-05-21 15:18:53.272553	1
4616	190	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:53.477203	2025-05-21 15:18:53.477208	1
4617	192	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:53.603836	2025-05-21 15:18:53.603838	1
4618	194	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:54.081244	2025-05-21 15:18:54.081249	1
4619	195	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:54.176382	2025-05-21 15:18:54.176388	1
4620	196	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:54.270878	2025-05-21 15:18:54.270884	1
4621	197	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:54.389291	2025-05-21 15:18:54.389302	1
4622	200	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:54.495348	2025-05-21 15:18:54.495353	1
4623	202	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:54.598202	2025-05-21 15:18:54.598207	1
4624	203	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:54.687628	2025-05-21 15:18:54.687633	1
4625	205	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:54.791625	2025-05-21 15:18:54.791629	1
4626	206	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:54.896439	2025-05-21 15:18:54.896445	1
4627	207	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:54.99319	2025-05-21 15:18:54.993194	1
4628	208	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:55.092204	2025-05-21 15:18:55.092208	1
4629	209	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:55.198537	2025-05-21 15:18:55.198541	1
4630	210	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:55.303547	2025-05-21 15:18:55.303552	1
4631	198	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:55.39182	2025-05-21 15:18:55.391825	1
4632	201	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:55.494243	2025-05-21 15:18:55.494248	1
4633	204	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:55.59808	2025-05-21 15:18:55.598085	1
4634	214	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:55.704763	2025-05-21 15:18:55.704768	1
4635	225	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:55.799693	2025-05-21 15:18:55.799696	1
4636	216	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:56.211759	2025-05-21 15:18:56.211764	1
4637	217	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:56.316912	2025-05-21 15:18:56.316917	1
4638	218	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:56.418489	2025-05-21 15:18:56.418493	1
4639	219	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:56.510449	2025-05-21 15:18:56.510454	1
4640	220	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:56.606424	2025-05-21 15:18:56.606428	1
4641	221	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:56.692835	2025-05-21 15:18:56.69284	1
4642	222	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:56.786349	2025-05-21 15:18:56.786351	1
4643	223	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:57.293814	2025-05-21 15:18:57.293819	1
4644	224	2025-05-21	\N	\N	present	\N	2025-05-21 15:18:57.400896	2025-05-21 15:18:57.400898	1
4645	184	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:53.658327	2025-05-22 07:52:53.658337	1
4646	185	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:53.765929	2025-05-22 07:52:53.765934	1
4647	186	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:53.858357	2025-05-22 07:52:53.858362	1
4648	187	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:53.952173	2025-05-22 07:52:53.952178	1
4649	188	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:54.04465	2025-05-22 07:52:54.044652	1
4650	180	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:54.467583	2025-05-22 07:52:54.467588	1
4651	181	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:54.56225	2025-05-22 07:52:54.562255	1
4652	179	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:54.654994	2025-05-22 07:52:54.654999	1
4653	178	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:54.749491	2025-05-22 07:52:54.749496	1
4654	182	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:54.842452	2025-05-22 07:52:54.842457	1
4655	175	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:54.935584	2025-05-22 07:52:54.935589	1
4656	173	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:55.028534	2025-05-22 07:52:55.028538	1
4657	172	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:55.121871	2025-05-22 07:52:55.121876	1
4658	171	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:55.214453	2025-05-22 07:52:55.214457	1
4659	174	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:55.307292	2025-05-22 07:52:55.307298	1
4660	177	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:55.39948	2025-05-22 07:52:55.399485	1
4661	169	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:55.491975	2025-05-22 07:52:55.49198	1
4662	183	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:55.58453	2025-05-22 07:52:55.584535	1
4663	226	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:55.679177	2025-05-22 07:52:55.679182	1
4664	227	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:55.772007	2025-05-22 07:52:55.772009	1
4665	193	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:56.185064	2025-05-22 07:52:56.185069	1
4666	191	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:56.277243	2025-05-22 07:52:56.277247	1
4667	189	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:56.369419	2025-05-22 07:52:56.369424	1
4668	190	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:56.461743	2025-05-22 07:52:56.461747	1
4669	192	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:56.55488	2025-05-22 07:52:56.554882	1
4670	194	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:56.968072	2025-05-22 07:52:56.968076	1
4671	195	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.061541	2025-05-22 07:52:57.061546	1
4672	196	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.154788	2025-05-22 07:52:57.154793	1
4673	197	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.247515	2025-05-22 07:52:57.247529	1
4674	200	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.339876	2025-05-22 07:52:57.339881	1
4675	202	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.432991	2025-05-22 07:52:57.432996	1
4676	203	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.525781	2025-05-22 07:52:57.525787	1
4677	205	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.618243	2025-05-22 07:52:57.618248	1
4678	206	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.711512	2025-05-22 07:52:57.711517	1
4679	207	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.803835	2025-05-22 07:52:57.80384	1
4680	208	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.896246	2025-05-22 07:52:57.896251	1
4681	209	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:57.988999	2025-05-22 07:52:57.989005	1
4682	210	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:58.081958	2025-05-22 07:52:58.081963	1
4683	198	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:58.174122	2025-05-22 07:52:58.174127	1
4684	201	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:58.266675	2025-05-22 07:52:58.26668	1
4685	204	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:58.363645	2025-05-22 07:52:58.36365	1
4686	214	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:58.45576	2025-05-22 07:52:58.455765	1
4687	225	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:58.549944	2025-05-22 07:52:58.549946	1
4688	216	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:58.964461	2025-05-22 07:52:58.964465	1
4689	217	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:59.057072	2025-05-22 07:52:59.057077	1
4690	218	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:59.15	2025-05-22 07:52:59.150006	1
4691	219	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:59.243291	2025-05-22 07:52:59.243296	1
4692	220	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:59.335431	2025-05-22 07:52:59.335436	1
4693	221	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:59.42777	2025-05-22 07:52:59.427776	1
4694	222	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:59.520144	2025-05-22 07:52:59.520146	1
4695	223	2025-05-22	\N	\N	present	\N	2025-05-22 07:52:59.933332	2025-05-22 07:52:59.933337	1
4696	224	2025-05-22	\N	\N	present	\N	2025-05-22 07:53:00.025256	2025-05-22 07:53:00.025258	1
4697	184	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:51.39327	2025-05-23 13:54:51.393274	1
4698	185	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:51.507387	2025-05-23 13:54:51.507392	1
4699	186	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:51.603355	2025-05-23 13:54:51.60336	1
4700	187	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:51.735523	2025-05-23 13:54:51.735528	1
4701	188	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:51.833202	2025-05-23 13:54:51.833204	1
4702	180	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:52.265293	2025-05-23 13:54:52.265298	1
4703	181	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:52.35778	2025-05-23 13:54:52.357785	1
4704	179	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:52.449231	2025-05-23 13:54:52.449236	1
4705	178	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:52.537711	2025-05-23 13:54:52.537716	1
4706	182	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:52.628309	2025-05-23 13:54:52.628314	1
4707	175	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:52.716847	2025-05-23 13:54:52.716852	1
4708	173	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:52.806278	2025-05-23 13:54:52.806283	1
4709	172	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:52.897007	2025-05-23 13:54:52.897012	1
4710	171	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:52.986992	2025-05-23 13:54:52.986997	1
4711	174	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:53.076308	2025-05-23 13:54:53.076312	1
4712	177	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:53.164935	2025-05-23 13:54:53.16494	1
4713	169	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:53.254138	2025-05-23 13:54:53.254143	1
4714	183	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:53.344216	2025-05-23 13:54:53.344221	1
4715	226	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:53.433163	2025-05-23 13:54:53.433167	1
4716	227	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:53.524925	2025-05-23 13:54:53.524926	1
4717	193	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:53.936883	2025-05-23 13:54:53.936888	1
4719	189	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:54.122715	2025-05-23 13:54:54.12272	1
4720	190	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:54.212548	2025-05-23 13:54:54.212552	1
4721	192	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:54.30389	2025-05-23 13:54:54.303892	1
4722	194	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:54.706134	2025-05-23 13:54:54.706139	1
4723	195	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:54.797092	2025-05-23 13:54:54.797097	1
4724	196	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:54.885889	2025-05-23 13:54:54.885894	1
4725	197	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:54.975568	2025-05-23 13:54:54.975573	1
4726	200	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:55.065514	2025-05-23 13:54:55.065519	1
4727	202	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:55.154911	2025-05-23 13:54:55.154915	1
4728	203	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:55.245801	2025-05-23 13:54:55.245806	1
4729	205	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:55.336625	2025-05-23 13:54:55.33663	1
4730	206	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:55.429674	2025-05-23 13:54:55.429684	1
4731	207	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:55.52868	2025-05-23 13:54:55.528684	1
4732	208	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:55.634426	2025-05-23 13:54:55.634431	1
4733	209	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:55.731204	2025-05-23 13:54:55.731209	1
4734	210	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:55.829005	2025-05-23 13:54:55.82901	1
4735	198	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:55.929422	2025-05-23 13:54:55.929427	1
4736	201	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:56.022215	2025-05-23 13:54:56.02222	1
4737	204	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:56.118952	2025-05-23 13:54:56.118957	1
4738	214	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:56.219154	2025-05-23 13:54:56.219158	1
4739	225	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:56.311706	2025-05-23 13:54:56.311707	1
4740	216	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:56.737049	2025-05-23 13:54:56.737054	1
4741	217	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:56.830534	2025-05-23 13:54:56.830539	1
4742	218	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:56.963764	2025-05-23 13:54:56.963769	1
4743	219	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:57.060073	2025-05-23 13:54:57.060078	1
4744	220	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:57.151269	2025-05-23 13:54:57.151274	1
4745	221	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:57.240771	2025-05-23 13:54:57.240776	1
4746	222	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:57.329467	2025-05-23 13:54:57.3295	1
4747	223	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:57.750466	2025-05-23 13:54:57.750471	1
4748	224	2025-05-23	\N	\N	present	\N	2025-05-23 13:54:57.854754	2025-05-23 13:54:57.854756	1
4749	184	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:43.30042	2025-05-26 10:44:43.300425	1
4750	185	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:43.39618	2025-05-26 10:44:43.396184	1
4751	186	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:43.482973	2025-05-26 10:44:43.482977	1
4752	187	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:43.569975	2025-05-26 10:44:43.56998	1
4753	188	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:43.657306	2025-05-26 10:44:43.657311	1
4754	184	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:43.744379	2025-05-26 10:44:43.744384	1
4755	185	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:43.831618	2025-05-26 10:44:43.831623	1
4756	186	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:43.918482	2025-05-26 10:44:43.918487	1
4757	187	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:44.005382	2025-05-26 10:44:44.005386	1
4758	188	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:44.092441	2025-05-26 10:44:44.092445	1
4759	184	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:44.191805	2025-05-26 10:44:44.19181	1
4760	185	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:44.284416	2025-05-26 10:44:44.284421	1
4761	186	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:44.371857	2025-05-26 10:44:44.371862	1
4762	187	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:44.459339	2025-05-26 10:44:44.459343	1
4763	188	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:44.549576	2025-05-26 10:44:44.549578	1
4764	180	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:45.647143	2025-05-26 10:44:45.647148	1
4765	181	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:45.734934	2025-05-26 10:44:45.734938	1
4766	179	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:45.82759	2025-05-26 10:44:45.827594	1
4767	178	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:45.914962	2025-05-26 10:44:45.914966	1
4768	182	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:46.004423	2025-05-26 10:44:46.004427	1
4770	173	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:46.181482	2025-05-26 10:44:46.181487	1
4771	172	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:46.270173	2025-05-26 10:44:46.270178	1
4772	171	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:46.357359	2025-05-26 10:44:46.357364	1
4773	174	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:46.447514	2025-05-26 10:44:46.447519	1
4774	177	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:46.534437	2025-05-26 10:44:46.534441	1
4775	169	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:46.621748	2025-05-26 10:44:46.621753	1
4776	183	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:46.711794	2025-05-26 10:44:46.711799	1
4777	226	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:46.799991	2025-05-26 10:44:46.799996	1
4778	227	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:46.889262	2025-05-26 10:44:46.889267	1
4779	180	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:46.980535	2025-05-26 10:44:46.980539	1
4780	181	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:47.070924	2025-05-26 10:44:47.070929	1
4781	179	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:47.162126	2025-05-26 10:44:47.162131	1
4782	178	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:47.261515	2025-05-26 10:44:47.261525	1
4783	182	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:47.356882	2025-05-26 10:44:47.356886	1
4785	173	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:47.538801	2025-05-26 10:44:47.538806	1
4786	172	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:47.631094	2025-05-26 10:44:47.631098	1
4787	171	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:47.718431	2025-05-26 10:44:47.718436	1
4788	174	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:47.808813	2025-05-26 10:44:47.808818	1
4789	177	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:47.908126	2025-05-26 10:44:47.90813	1
4790	169	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:48.000063	2025-05-26 10:44:48.000068	1
4791	183	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:48.096589	2025-05-26 10:44:48.096593	1
4792	226	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:48.184176	2025-05-26 10:44:48.18418	1
4793	227	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:48.272134	2025-05-26 10:44:48.272139	1
4794	180	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:48.359141	2025-05-26 10:44:48.359146	1
4795	181	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:48.446605	2025-05-26 10:44:48.446609	1
4796	179	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:48.534505	2025-05-26 10:44:48.534509	1
4797	178	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:48.621233	2025-05-26 10:44:48.621238	1
4798	182	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:48.710628	2025-05-26 10:44:48.710633	1
4799	175	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:48.797392	2025-05-26 10:44:48.797397	1
4800	173	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:48.884164	2025-05-26 10:44:48.884169	1
4801	172	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:48.971266	2025-05-26 10:44:48.971271	1
4802	171	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:49.058642	2025-05-26 10:44:49.058646	1
4803	174	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:49.145705	2025-05-26 10:44:49.14571	1
4804	177	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:49.242717	2025-05-26 10:44:49.242721	1
4805	169	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:49.344962	2025-05-26 10:44:49.344966	1
4806	183	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:49.432106	2025-05-26 10:44:49.43211	1
4807	226	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:49.519397	2025-05-26 10:44:49.519402	1
4808	227	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:49.609929	2025-05-26 10:44:49.60993	1
4809	193	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:50.253393	2025-05-26 10:44:50.253399	1
4810	191	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:50.34381	2025-05-26 10:44:50.343815	1
4811	189	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:50.437343	2025-05-26 10:44:50.437348	1
4812	190	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:50.528365	2025-05-26 10:44:50.52837	1
4813	192	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:50.61972	2025-05-26 10:44:50.619724	1
4814	193	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:50.713056	2025-05-26 10:44:50.71306	1
4815	191	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:50.80423	2025-05-26 10:44:50.804235	1
4816	189	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:50.904908	2025-05-26 10:44:50.904913	1
4817	190	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:50.998934	2025-05-26 10:44:50.998939	1
4818	192	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:51.093438	2025-05-26 10:44:51.093443	1
4819	193	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:51.186637	2025-05-26 10:44:51.186641	1
4820	191	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:51.277487	2025-05-26 10:44:51.277492	1
4821	189	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:51.36651	2025-05-26 10:44:51.366515	1
4822	190	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:51.466459	2025-05-26 10:44:51.466464	1
4823	192	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:51.560406	2025-05-26 10:44:51.560408	1
4824	194	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:52.799422	2025-05-26 10:44:52.799427	1
4784	175	2025-05-25	\N	\N	present		2025-05-26 10:44:47.449526	2025-05-28 07:30:04.274251	1
4825	195	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:52.897029	2025-05-26 10:44:52.897034	1
4826	196	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:52.99724	2025-05-26 10:44:52.997244	1
4827	197	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:53.090977	2025-05-26 10:44:53.090982	1
4828	200	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:53.180648	2025-05-26 10:44:53.180652	1
4829	202	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:53.268241	2025-05-26 10:44:53.268246	1
4830	203	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:53.357847	2025-05-26 10:44:53.357851	1
4831	205	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:53.446321	2025-05-26 10:44:53.446326	1
4832	206	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:53.53726	2025-05-26 10:44:53.537265	1
4833	207	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:53.62787	2025-05-26 10:44:53.627875	1
4834	208	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:53.717159	2025-05-26 10:44:53.717164	1
4835	209	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:53.807777	2025-05-26 10:44:53.807781	1
4836	210	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:53.902424	2025-05-26 10:44:53.902429	1
4837	198	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:54.001129	2025-05-26 10:44:54.001134	1
4838	201	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:54.092753	2025-05-26 10:44:54.092758	1
4839	204	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:54.183617	2025-05-26 10:44:54.183622	1
4840	214	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:54.271838	2025-05-26 10:44:54.271842	1
4841	225	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:54.362932	2025-05-26 10:44:54.362937	1
4842	194	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:54.451489	2025-05-26 10:44:54.451493	1
4843	195	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:54.539589	2025-05-26 10:44:54.539593	1
4844	196	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:54.630773	2025-05-26 10:44:54.630778	1
4845	197	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:54.717465	2025-05-26 10:44:54.71747	1
4846	200	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:54.804815	2025-05-26 10:44:54.80482	1
4847	202	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:54.894453	2025-05-26 10:44:54.894458	1
4848	203	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:54.983871	2025-05-26 10:44:54.983875	1
4849	205	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:55.081977	2025-05-26 10:44:55.081982	1
4850	206	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:55.171133	2025-05-26 10:44:55.171138	1
4851	207	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:55.262898	2025-05-26 10:44:55.262903	1
4852	208	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:55.349647	2025-05-26 10:44:55.349651	1
4853	209	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:55.437916	2025-05-26 10:44:55.437921	1
4854	210	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:55.529926	2025-05-26 10:44:55.52993	1
4855	198	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:55.619	2025-05-26 10:44:55.619005	1
4856	201	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:55.720195	2025-05-26 10:44:55.720199	1
4857	204	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:55.821014	2025-05-26 10:44:55.821019	1
4858	214	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:55.914948	2025-05-26 10:44:55.914952	1
4859	225	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:56.007728	2025-05-26 10:44:56.007733	1
4860	194	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:56.104798	2025-05-26 10:44:56.104802	1
4861	195	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:56.203809	2025-05-26 10:44:56.203814	1
4862	196	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:56.294871	2025-05-26 10:44:56.294876	1
4863	197	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:56.382308	2025-05-26 10:44:56.382313	1
4864	200	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:56.474055	2025-05-26 10:44:56.474061	1
4865	202	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:56.564084	2025-05-26 10:44:56.56411	1
4866	203	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:56.6609	2025-05-26 10:44:56.660905	1
4867	205	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:56.748998	2025-05-26 10:44:56.749003	1
4868	206	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:56.83637	2025-05-26 10:44:56.836375	1
4869	207	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:56.923446	2025-05-26 10:44:56.92345	1
4870	208	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:57.014136	2025-05-26 10:44:57.014141	1
4871	209	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:57.108723	2025-05-26 10:44:57.108728	1
4872	210	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:57.196002	2025-05-26 10:44:57.196007	1
4873	198	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:57.288083	2025-05-26 10:44:57.288088	1
4874	201	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:57.38378	2025-05-26 10:44:57.383785	1
4875	204	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:57.475155	2025-05-26 10:44:57.47516	1
4876	214	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:57.563836	2025-05-26 10:44:57.563841	1
4877	225	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:57.651794	2025-05-26 10:44:57.651796	1
4878	216	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:58.351398	2025-05-26 10:44:58.351403	1
4879	217	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:58.441905	2025-05-26 10:44:58.44191	1
4880	218	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:58.531297	2025-05-26 10:44:58.531301	1
4881	219	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:58.629301	2025-05-26 10:44:58.629306	1
4882	220	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:58.721273	2025-05-26 10:44:58.721278	1
4883	221	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:58.810758	2025-05-26 10:44:58.810762	1
4884	222	2025-05-24	\N	\N	present	\N	2025-05-26 10:44:58.899768	2025-05-26 10:44:58.899773	1
4885	216	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:58.992279	2025-05-26 10:44:58.992292	1
4886	217	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:59.080716	2025-05-26 10:44:59.080721	1
4887	218	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:59.16824	2025-05-26 10:44:59.168245	1
4888	219	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:59.25643	2025-05-26 10:44:59.256434	1
4889	220	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:59.343309	2025-05-26 10:44:59.343313	1
4890	221	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:59.430386	2025-05-26 10:44:59.430391	1
4891	222	2025-05-25	\N	\N	present	\N	2025-05-26 10:44:59.517623	2025-05-26 10:44:59.517627	1
4892	216	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:59.605263	2025-05-26 10:44:59.605267	1
4893	217	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:59.695666	2025-05-26 10:44:59.695671	1
4894	218	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:59.783002	2025-05-26 10:44:59.783007	1
4895	219	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:59.870764	2025-05-26 10:44:59.87078	1
4896	220	2025-05-26	\N	\N	present	\N	2025-05-26 10:44:59.958288	2025-05-26 10:44:59.958293	1
4897	221	2025-05-26	\N	\N	present	\N	2025-05-26 10:45:00.049412	2025-05-26 10:45:00.049417	1
4898	222	2025-05-26	\N	\N	present	\N	2025-05-26 10:45:00.145985	2025-05-26 10:45:00.145987	1
4899	223	2025-05-24	\N	\N	present	\N	2025-05-26 10:45:00.651355	2025-05-26 10:45:00.65136	1
4900	224	2025-05-24	\N	\N	present	\N	2025-05-26 10:45:00.738222	2025-05-26 10:45:00.738227	1
4901	223	2025-05-25	\N	\N	present	\N	2025-05-26 10:45:00.825938	2025-05-26 10:45:00.825943	1
4902	224	2025-05-25	\N	\N	present	\N	2025-05-26 10:45:00.929537	2025-05-26 10:45:00.929541	1
4903	223	2025-05-26	\N	\N	present	\N	2025-05-26 10:45:01.018766	2025-05-26 10:45:01.018771	1
4904	224	2025-05-26	\N	\N	present	\N	2025-05-26 10:45:01.107792	2025-05-26 10:45:01.107794	1
4905	184	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:01.011597	2025-05-28 07:30:01.011603	1
4906	185	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:01.106069	2025-05-28 07:30:01.106075	1
4907	186	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:01.188366	2025-05-28 07:30:01.188373	1
4908	187	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:01.270387	2025-05-28 07:30:01.270394	1
4909	188	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:01.35271	2025-05-28 07:30:01.352716	1
4910	184	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:01.435031	2025-05-28 07:30:01.435037	1
4911	185	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:01.516965	2025-05-28 07:30:01.516971	1
4912	186	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:01.598503	2025-05-28 07:30:01.598509	1
4913	187	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:01.68503	2025-05-28 07:30:01.685037	1
4914	188	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:01.766468	2025-05-28 07:30:01.76647	1
4769	175	2025-05-24	\N	\N	present	حالة صرع 	2025-05-26 10:44:46.09417	2025-05-28 07:30:03.607085	1
4915	180	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:05.418583	2025-05-28 07:30:05.418589	1
4916	181	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:05.503573	2025-05-28 07:30:05.50358	1
4917	179	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:05.585625	2025-05-28 07:30:05.585631	1
4918	178	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:05.667428	2025-05-28 07:30:05.667435	1
4919	182	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:05.749155	2025-05-28 07:30:05.749161	1
4921	173	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:05.912846	2025-05-28 07:30:05.912853	1
4922	172	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:05.995677	2025-05-28 07:30:05.995684	1
4923	171	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:06.077183	2025-05-28 07:30:06.077189	1
4924	174	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:06.159713	2025-05-28 07:30:06.15972	1
4925	177	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:06.242411	2025-05-28 07:30:06.242418	1
4926	169	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:06.325067	2025-05-28 07:30:06.325079	1
4927	183	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:06.407131	2025-05-28 07:30:06.407137	1
4928	226	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:06.489113	2025-05-28 07:30:06.48912	1
4929	227	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:06.572033	2025-05-28 07:30:06.572039	1
4920	175	2025-05-27	\N	\N	sick	نوبة صرع	2025-05-28 07:30:05.830415	2025-05-28 07:31:11.718235	1
4930	180	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:06.654272	2025-05-28 07:30:06.65428	1
4931	181	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:06.738535	2025-05-28 07:30:06.738542	1
4932	179	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:06.822112	2025-05-28 07:30:06.822118	1
4933	178	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:06.904423	2025-05-28 07:30:06.90443	1
4934	182	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:06.986632	2025-05-28 07:30:06.986638	1
4936	173	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:07.150263	2025-05-28 07:30:07.15027	1
4937	172	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:07.23262	2025-05-28 07:30:07.232626	1
4938	171	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:07.314639	2025-05-28 07:30:07.314646	1
4939	174	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:07.396366	2025-05-28 07:30:07.396373	1
4940	177	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:07.478551	2025-05-28 07:30:07.478557	1
4941	169	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:07.561806	2025-05-28 07:30:07.561812	1
4942	183	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:07.64654	2025-05-28 07:30:07.646547	1
4943	226	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:07.727998	2025-05-28 07:30:07.728004	1
4944	227	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:07.809537	2025-05-28 07:30:07.809543	1
4945	193	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:09.300658	2025-05-28 07:30:09.300664	1
4946	191	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:09.381916	2025-05-28 07:30:09.381922	1
4947	189	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:09.46353	2025-05-28 07:30:09.463536	1
4948	190	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:09.545534	2025-05-28 07:30:09.54554	1
4949	192	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:09.62765	2025-05-28 07:30:09.627655	1
4950	193	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:09.708935	2025-05-28 07:30:09.708941	1
4951	191	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:09.79169	2025-05-28 07:30:09.791696	1
4952	189	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:09.873167	2025-05-28 07:30:09.873174	1
4953	190	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:09.957132	2025-05-28 07:30:09.957138	1
4954	192	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:10.039142	2025-05-28 07:30:10.039144	1
4955	194	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.164067	2025-05-28 07:30:14.164074	1
4956	195	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.245835	2025-05-28 07:30:14.245841	1
4957	196	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.327584	2025-05-28 07:30:14.32759	1
4958	197	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.409082	2025-05-28 07:30:14.409088	1
4959	200	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.490548	2025-05-28 07:30:14.490553	1
4960	202	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.572686	2025-05-28 07:30:14.572693	1
4961	203	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.655172	2025-05-28 07:30:14.655179	1
4962	205	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.736965	2025-05-28 07:30:14.736972	1
4963	206	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.818277	2025-05-28 07:30:14.818284	1
4964	207	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.900524	2025-05-28 07:30:14.90053	1
4965	208	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:14.98212	2025-05-28 07:30:14.982127	1
4966	209	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:15.063476	2025-05-28 07:30:15.063482	1
4967	210	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:15.145948	2025-05-28 07:30:15.145955	1
4968	198	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:15.228008	2025-05-28 07:30:15.228015	1
4969	201	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:15.31001	2025-05-28 07:30:15.310017	1
4970	204	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:15.392033	2025-05-28 07:30:15.392039	1
4971	214	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:15.474873	2025-05-28 07:30:15.474879	1
4972	225	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:15.557073	2025-05-28 07:30:15.557078	1
4973	194	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:15.641693	2025-05-28 07:30:15.641701	1
4974	195	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:15.723796	2025-05-28 07:30:15.723803	1
4975	196	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:15.809883	2025-05-28 07:30:15.809889	1
4976	197	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:15.891791	2025-05-28 07:30:15.891798	1
4977	200	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:15.975173	2025-05-28 07:30:15.975181	1
4978	202	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.059124	2025-05-28 07:30:16.059131	1
4979	203	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.141259	2025-05-28 07:30:16.141265	1
4980	205	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.224517	2025-05-28 07:30:16.224523	1
4981	206	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.307014	2025-05-28 07:30:16.30702	1
4982	207	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.388835	2025-05-28 07:30:16.388841	1
4983	208	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.472211	2025-05-28 07:30:16.472217	1
4984	209	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.560402	2025-05-28 07:30:16.560409	1
4985	210	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.646878	2025-05-28 07:30:16.646884	1
4986	198	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.731661	2025-05-28 07:30:16.731668	1
4987	201	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.815309	2025-05-28 07:30:16.815326	1
4988	204	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.899431	2025-05-28 07:30:16.899437	1
4989	214	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:16.998008	2025-05-28 07:30:16.998014	1
4990	225	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:17.087654	2025-05-28 07:30:17.087657	1
4991	216	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:18.952275	2025-05-28 07:30:18.952282	1
4992	217	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:19.034139	2025-05-28 07:30:19.034145	1
4993	218	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:19.116542	2025-05-28 07:30:19.116549	1
4994	219	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:19.199359	2025-05-28 07:30:19.199402	1
4995	220	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:19.280858	2025-05-28 07:30:19.280863	1
4996	221	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:19.36278	2025-05-28 07:30:19.362786	1
4997	222	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:19.444397	2025-05-28 07:30:19.444414	1
4998	216	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:19.526057	2025-05-28 07:30:19.526063	1
4999	217	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:19.607678	2025-05-28 07:30:19.607684	1
5000	218	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:19.689246	2025-05-28 07:30:19.689252	1
5001	219	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:19.771834	2025-05-28 07:30:19.771841	1
5002	220	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:19.853383	2025-05-28 07:30:19.85339	1
5003	221	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:19.93485	2025-05-28 07:30:19.934856	1
5004	222	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:20.016867	2025-05-28 07:30:20.016869	1
5005	223	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:20.797975	2025-05-28 07:30:20.797981	1
5006	224	2025-05-27	\N	\N	present	\N	2025-05-28 07:30:20.879662	2025-05-28 07:30:20.879667	1
5007	223	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:20.96123	2025-05-28 07:30:20.961236	1
5008	224	2025-05-28	\N	\N	present	\N	2025-05-28 07:30:21.042852	2025-05-28 07:30:21.042854	1
4935	175	2025-05-28	\N	\N	sick	نوبة صرع	2025-05-28 07:30:07.068339	2025-05-28 07:31:59.228127	1
5009	184	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:26.288746	2025-05-29 10:25:26.28875	1
5010	185	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:26.39054	2025-05-29 10:25:26.390546	1
5011	186	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:26.478552	2025-05-29 10:25:26.478556	1
5012	187	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:26.564992	2025-05-29 10:25:26.564997	1
5013	188	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:26.651791	2025-05-29 10:25:26.651799	1
5014	180	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.05195	2025-05-29 10:25:27.051955	1
5015	181	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.138514	2025-05-29 10:25:27.138519	1
5016	179	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.22663	2025-05-29 10:25:27.226635	1
5017	178	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.313161	2025-05-29 10:25:27.313166	1
5018	182	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.399853	2025-05-29 10:25:27.399858	1
5019	175	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.488797	2025-05-29 10:25:27.488802	1
5020	173	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.575348	2025-05-29 10:25:27.575354	1
5021	172	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.662341	2025-05-29 10:25:27.662346	1
5022	171	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.748895	2025-05-29 10:25:27.7489	1
5023	174	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.835578	2025-05-29 10:25:27.835583	1
5024	177	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:27.921918	2025-05-29 10:25:27.921923	1
5025	169	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:28.008291	2025-05-29 10:25:28.008296	1
5026	183	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:28.094946	2025-05-29 10:25:28.094951	1
5027	226	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:28.181841	2025-05-29 10:25:28.181846	1
5028	227	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:28.26847	2025-05-29 10:25:28.268472	1
5029	193	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:28.657566	2025-05-29 10:25:28.657571	1
5030	191	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:28.744282	2025-05-29 10:25:28.744316	1
5031	189	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:28.831772	2025-05-29 10:25:28.831776	1
5032	190	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:28.918205	2025-05-29 10:25:28.91821	1
5033	192	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:29.00502	2025-05-29 10:25:29.005022	1
5034	194	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:29.39006	2025-05-29 10:25:29.390065	1
5035	195	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:29.476704	2025-05-29 10:25:29.476709	1
5036	196	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:29.576945	2025-05-29 10:25:29.576949	1
5038	200	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:29.750372	2025-05-29 10:25:29.750377	1
5039	202	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:29.837232	2025-05-29 10:25:29.837237	1
5040	203	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:29.975104	2025-05-29 10:25:29.975109	1
5041	205	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.06151	2025-05-29 10:25:30.061515	1
5042	206	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.147988	2025-05-29 10:25:30.147993	1
5043	207	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.234377	2025-05-29 10:25:30.234382	1
5044	208	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.320656	2025-05-29 10:25:30.320666	1
5045	209	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.407088	2025-05-29 10:25:30.407093	1
5046	210	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.494165	2025-05-29 10:25:30.494169	1
5047	198	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.580772	2025-05-29 10:25:30.580777	1
5048	201	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.667143	2025-05-29 10:25:30.667148	1
5049	204	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.754269	2025-05-29 10:25:30.754274	1
5050	214	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.840826	2025-05-29 10:25:30.84083	1
5051	225	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:30.927783	2025-05-29 10:25:30.927786	1
5052	216	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:31.317852	2025-05-29 10:25:31.317856	1
5053	217	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:31.405629	2025-05-29 10:25:31.405634	1
5054	218	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:31.491856	2025-05-29 10:25:31.491861	1
5055	219	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:31.578329	2025-05-29 10:25:31.578333	1
5056	220	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:31.664731	2025-05-29 10:25:31.664737	1
5057	221	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:31.751266	2025-05-29 10:25:31.751271	1
5058	222	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:31.837105	2025-05-29 10:25:31.837107	1
5059	223	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:32.222433	2025-05-29 10:25:32.222438	1
5060	224	2025-05-29	\N	\N	present	\N	2025-05-29 10:25:32.308843	2025-05-29 10:25:32.308844	1
5061	184	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:01.044519	2025-05-31 08:08:01.044524	1
5062	185	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:01.15543	2025-05-31 08:08:01.155435	1
5063	186	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:01.246979	2025-05-31 08:08:01.246984	1
5064	187	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:01.338962	2025-05-31 08:08:01.338967	1
5065	188	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:01.432366	2025-05-31 08:08:01.432371	1
5066	184	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:01.52318	2025-05-31 08:08:01.523185	1
5067	185	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:01.614577	2025-05-31 08:08:01.614582	1
5068	186	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:01.707679	2025-05-31 08:08:01.707685	1
5069	187	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:01.802993	2025-05-31 08:08:01.802997	1
5070	188	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:01.89375	2025-05-31 08:08:01.893753	1
5071	181	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.005854	2025-05-31 08:08:03.005858	1
5072	179	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.098984	2025-05-31 08:08:03.09899	1
5073	178	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.18984	2025-05-31 08:08:03.189844	1
5074	180	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.284355	2025-05-31 08:08:03.28436	1
5075	182	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.37524	2025-05-31 08:08:03.375244	1
5076	175	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.466158	2025-05-31 08:08:03.466163	1
5077	173	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.558102	2025-05-31 08:08:03.558106	1
5078	172	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.65169	2025-05-31 08:08:03.651695	1
5079	171	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.748187	2025-05-31 08:08:03.748191	1
5080	174	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.844061	2025-05-31 08:08:03.844066	1
5081	177	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:03.935719	2025-05-31 08:08:03.935723	1
5082	169	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:04.026986	2025-05-31 08:08:04.026991	1
5083	183	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:04.122799	2025-05-31 08:08:04.122804	1
5084	226	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:04.21817	2025-05-31 08:08:04.218175	1
5085	227	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:04.310421	2025-05-31 08:08:04.310426	1
5086	181	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:04.402082	2025-05-31 08:08:04.402086	1
5087	179	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:04.49379	2025-05-31 08:08:04.493794	1
5088	178	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:04.584953	2025-05-31 08:08:04.584959	1
5089	180	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:04.675567	2025-05-31 08:08:04.675571	1
5090	182	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:04.767224	2025-05-31 08:08:04.767228	1
5092	173	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:04.950961	2025-05-31 08:08:04.950966	1
5093	172	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:05.042683	2025-05-31 08:08:05.042688	1
5094	171	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:05.134405	2025-05-31 08:08:05.13441	1
5095	174	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:05.225677	2025-05-31 08:08:05.225681	1
5096	177	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:05.316316	2025-05-31 08:08:05.31632	1
5097	169	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:05.407092	2025-05-31 08:08:05.407096	1
5098	183	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:05.498357	2025-05-31 08:08:05.498362	1
5099	226	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:05.592407	2025-05-31 08:08:05.592412	1
5100	227	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:05.683347	2025-05-31 08:08:05.68335	1
5101	193	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:06.331957	2025-05-31 08:08:06.331961	1
5102	191	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:06.4232	2025-05-31 08:08:06.423205	1
5103	189	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:06.514361	2025-05-31 08:08:06.514366	1
5104	190	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:06.613983	2025-05-31 08:08:06.613988	1
5105	192	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:06.706348	2025-05-31 08:08:06.706353	1
5106	193	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:06.798993	2025-05-31 08:08:06.798998	1
5107	191	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:06.891796	2025-05-31 08:08:06.891801	1
5108	189	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:06.989388	2025-05-31 08:08:06.989393	1
5109	190	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:07.080986	2025-05-31 08:08:07.080992	1
5110	192	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:07.172478	2025-05-31 08:08:07.17248	1
5111	194	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:08.427582	2025-05-31 08:08:08.427586	1
5112	195	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:08.525848	2025-05-31 08:08:08.525853	1
5113	196	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:08.61669	2025-05-31 08:08:08.616695	1
5114	197	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:08.707938	2025-05-31 08:08:08.707942	1
5115	200	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:08.799274	2025-05-31 08:08:08.799278	1
5116	202	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:08.890399	2025-05-31 08:08:08.890404	1
5117	203	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:08.981286	2025-05-31 08:08:08.98129	1
5118	205	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:09.07263	2025-05-31 08:08:09.072634	1
5119	206	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:09.164234	2025-05-31 08:08:09.164239	1
5120	207	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:09.257357	2025-05-31 08:08:09.257361	1
5121	208	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:09.353001	2025-05-31 08:08:09.353006	1
5122	209	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:09.445794	2025-05-31 08:08:09.445799	1
5123	210	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:09.538354	2025-05-31 08:08:09.538358	1
5124	198	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:09.630075	2025-05-31 08:08:09.63008	1
5125	201	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:09.721268	2025-05-31 08:08:09.721273	1
5126	204	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:09.814239	2025-05-31 08:08:09.814245	1
5127	214	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:09.906854	2025-05-31 08:08:09.906859	1
5128	225	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:10.001328	2025-05-31 08:08:10.001333	1
5129	194	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:10.09223	2025-05-31 08:08:10.092234	1
5130	195	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:10.184139	2025-05-31 08:08:10.184144	1
5131	196	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:10.275363	2025-05-31 08:08:10.275367	1
5132	197	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:10.369614	2025-05-31 08:08:10.369618	1
5133	200	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:10.463118	2025-05-31 08:08:10.463123	1
5134	202	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:10.55542	2025-05-31 08:08:10.555424	1
5135	203	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:10.647827	2025-05-31 08:08:10.647833	1
5136	205	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:10.73866	2025-05-31 08:08:10.738665	1
5137	206	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:10.831322	2025-05-31 08:08:10.831327	1
5138	207	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:10.922434	2025-05-31 08:08:10.922438	1
5139	208	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:11.015961	2025-05-31 08:08:11.015966	1
5140	209	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:11.111608	2025-05-31 08:08:11.111613	1
5141	210	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:11.203175	2025-05-31 08:08:11.20318	1
5142	198	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:11.294511	2025-05-31 08:08:11.294515	1
5143	201	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:11.386016	2025-05-31 08:08:11.386021	1
5144	204	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:11.477005	2025-05-31 08:08:11.477009	1
5145	214	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:11.569036	2025-05-31 08:08:11.569041	1
5146	225	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:11.659879	2025-05-31 08:08:11.659881	1
5147	216	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:12.402295	2025-05-31 08:08:12.4023	1
5148	217	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:12.492979	2025-05-31 08:08:12.492984	1
5149	218	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:12.58453	2025-05-31 08:08:12.584552	1
5150	219	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:12.677663	2025-05-31 08:08:12.677668	1
5151	220	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:12.769096	2025-05-31 08:08:12.769101	1
5152	221	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:12.859589	2025-05-31 08:08:12.859595	1
5153	222	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:12.950398	2025-05-31 08:08:12.950402	1
5154	216	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:13.04173	2025-05-31 08:08:13.041735	1
5155	217	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:13.134933	2025-05-31 08:08:13.134938	1
5156	218	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:13.226353	2025-05-31 08:08:13.226357	1
5157	219	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:13.317365	2025-05-31 08:08:13.317369	1
5158	220	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:13.408336	2025-05-31 08:08:13.408341	1
5159	221	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:13.499158	2025-05-31 08:08:13.499162	1
5160	222	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:13.601081	2025-05-31 08:08:13.601083	1
5161	223	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:14.105908	2025-05-31 08:08:14.105913	1
5162	224	2025-05-30	\N	\N	present	\N	2025-05-31 08:08:14.205966	2025-05-31 08:08:14.20597	1
5163	223	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:14.297222	2025-05-31 08:08:14.297227	1
5164	224	2025-05-31	\N	\N	present	\N	2025-05-31 08:08:14.38788	2025-05-31 08:08:14.387882	1
4241	226	2025-05-14	\N	\N	sick		2025-05-14 11:01:41.404744	2025-05-31 09:22:07.20636	1
5091	175	2025-05-31	\N	\N	present		2025-05-31 08:08:04.857894	2025-05-31 11:26:38.120069	1
5428	184	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:27.836708	2025-06-02 15:00:27.836713	1
5429	185	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:27.927263	2025-06-02 15:00:27.927268	1
5430	186	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:28.017254	2025-06-02 15:00:28.017258	1
5431	187	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:28.106678	2025-06-02 15:00:28.106683	1
5432	188	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:28.197064	2025-06-02 15:00:28.197068	1
5433	184	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:28.291778	2025-06-02 15:00:28.291783	1
5434	185	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:28.384396	2025-06-02 15:00:28.3844	1
5435	186	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:28.487167	2025-06-02 15:00:28.487172	1
5436	187	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:28.585355	2025-06-02 15:00:28.58536	1
5437	188	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:28.676277	2025-06-02 15:00:28.676278	1
5438	181	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:29.093303	2025-06-02 15:00:29.093308	1
5439	179	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:29.182803	2025-06-02 15:00:29.182808	1
5440	178	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:29.271778	2025-06-02 15:00:29.271783	1
5441	180	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:29.361636	2025-06-02 15:00:29.36164	1
5442	182	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:29.451408	2025-06-02 15:00:29.451413	1
5443	175	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:29.541268	2025-06-02 15:00:29.541272	1
5444	173	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:29.631159	2025-06-02 15:00:29.631163	1
5445	172	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:29.720017	2025-06-02 15:00:29.720021	1
5446	171	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:29.81232	2025-06-02 15:00:29.812325	1
5447	174	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:29.909674	2025-06-02 15:00:29.909679	1
5448	177	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:30.007636	2025-06-02 15:00:30.00764	1
5449	169	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:30.099789	2025-06-02 15:00:30.099794	1
5450	183	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:30.197335	2025-06-02 15:00:30.197339	1
5451	226	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:30.290991	2025-06-02 15:00:30.290996	1
5452	227	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:30.380417	2025-06-02 15:00:30.380421	1
5453	181	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:30.469468	2025-06-02 15:00:30.469473	1
5454	179	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:30.55961	2025-06-02 15:00:30.559614	1
5455	178	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:30.650319	2025-06-02 15:00:30.650324	1
5456	180	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:30.740382	2025-06-02 15:00:30.740386	1
5457	182	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:30.830226	2025-06-02 15:00:30.830231	1
5458	175	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:30.922574	2025-06-02 15:00:30.922579	1
5459	173	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:31.013463	2025-06-02 15:00:31.013468	1
5460	172	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:31.110047	2025-06-02 15:00:31.110051	1
5461	171	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:31.199143	2025-06-02 15:00:31.199148	1
5462	174	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:31.291132	2025-06-02 15:00:31.291136	1
5463	177	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:31.387915	2025-06-02 15:00:31.387919	1
5464	169	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:31.477967	2025-06-02 15:00:31.477972	1
5465	183	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:31.567974	2025-06-02 15:00:31.567979	1
5466	226	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:31.656885	2025-06-02 15:00:31.65689	1
5467	227	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:31.747357	2025-06-02 15:00:31.747358	1
5468	193	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:32.150854	2025-06-02 15:00:32.150859	1
5469	191	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:32.240494	2025-06-02 15:00:32.240499	1
5470	189	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:32.329765	2025-06-02 15:00:32.32977	1
5471	190	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:32.418561	2025-06-02 15:00:32.418566	1
5472	192	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:32.509186	2025-06-02 15:00:32.50919	1
5473	193	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:32.598447	2025-06-02 15:00:32.598452	1
5474	191	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:32.691415	2025-06-02 15:00:32.69142	1
5475	189	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:32.782271	2025-06-02 15:00:32.782276	1
5476	190	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:32.872729	2025-06-02 15:00:32.872734	1
5477	192	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:32.962271	2025-06-02 15:00:32.962272	1
5478	194	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:33.364263	2025-06-02 15:00:33.364268	1
5479	195	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:33.455878	2025-06-02 15:00:33.455883	1
5480	196	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:33.546797	2025-06-02 15:00:33.546802	1
5481	197	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:33.636564	2025-06-02 15:00:33.636569	1
5482	200	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:33.727156	2025-06-02 15:00:33.727161	1
5483	202	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:33.817472	2025-06-02 15:00:33.817477	1
5484	203	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:33.908152	2025-06-02 15:00:33.908157	1
5485	205	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.009406	2025-06-02 15:00:34.00941	1
5486	206	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.100278	2025-06-02 15:00:34.100283	1
5487	207	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.189109	2025-06-02 15:00:34.189113	1
5488	208	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.278573	2025-06-02 15:00:34.278577	1
5489	209	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.369539	2025-06-02 15:00:34.369544	1
5490	198	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.466438	2025-06-02 15:00:34.466443	1
5491	201	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.555644	2025-06-02 15:00:34.555648	1
5492	204	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.64611	2025-06-02 15:00:34.646114	1
5493	214	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.736575	2025-06-02 15:00:34.73658	1
5494	225	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.82916	2025-06-02 15:00:34.829165	1
5495	230	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:34.91943	2025-06-02 15:00:34.919435	1
5496	231	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:35.008492	2025-06-02 15:00:35.008496	1
5497	194	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.097752	2025-06-02 15:00:35.097757	1
5498	195	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.187125	2025-06-02 15:00:35.18713	1
5499	196	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.276395	2025-06-02 15:00:35.2764	1
5500	197	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.366451	2025-06-02 15:00:35.366455	1
5501	200	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.455361	2025-06-02 15:00:35.455366	1
5502	202	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.544752	2025-06-02 15:00:35.544757	1
5503	203	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.636693	2025-06-02 15:00:35.636698	1
5504	205	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.728146	2025-06-02 15:00:35.72815	1
5505	206	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.817533	2025-06-02 15:00:35.817538	1
5506	207	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.907168	2025-06-02 15:00:35.907172	1
5507	208	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:35.998177	2025-06-02 15:00:35.998182	1
5508	209	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:36.087338	2025-06-02 15:00:36.087343	1
5509	198	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:36.176485	2025-06-02 15:00:36.17649	1
5510	201	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:36.266362	2025-06-02 15:00:36.266366	1
5511	204	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:36.35578	2025-06-02 15:00:36.355785	1
5512	214	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:36.445955	2025-06-02 15:00:36.44596	1
5513	225	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:36.535231	2025-06-02 15:00:36.535236	1
5514	230	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:36.62422	2025-06-02 15:00:36.624225	1
5515	231	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:36.715254	2025-06-02 15:00:36.715256	1
5516	216	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:37.217277	2025-06-02 15:00:37.217281	1
5517	217	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:37.306965	2025-06-02 15:00:37.30697	1
5518	218	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:37.396043	2025-06-02 15:00:37.396048	1
5519	219	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:37.486019	2025-06-02 15:00:37.486024	1
5520	220	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:37.577098	2025-06-02 15:00:37.577103	1
5521	221	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:37.668488	2025-06-02 15:00:37.668493	1
5522	222	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:37.760619	2025-06-02 15:00:37.760623	1
5523	216	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:37.850413	2025-06-02 15:00:37.850418	1
5524	217	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:37.940384	2025-06-02 15:00:37.94039	1
5525	218	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:38.029571	2025-06-02 15:00:38.029576	1
5526	219	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:38.121834	2025-06-02 15:00:38.121838	1
5527	220	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:38.213613	2025-06-02 15:00:38.213618	1
5528	221	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:38.317281	2025-06-02 15:00:38.317286	1
5529	222	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:38.421803	2025-06-02 15:00:38.421804	1
5530	223	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:38.837856	2025-06-02 15:00:38.837861	1
5531	224	2025-06-01	\N	\N	present	\N	2025-06-02 15:00:38.927859	2025-06-02 15:00:38.927864	1
5532	223	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:39.019766	2025-06-02 15:00:39.01977	1
5533	224	2025-06-02	\N	\N	present	\N	2025-06-02 15:00:39.109559	2025-06-02 15:00:39.109561	1
5587	184	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:46.96394	2025-06-03 09:53:46.963945	1
5588	185	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:47.054292	2025-06-03 09:53:47.054296	1
5589	186	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:47.143919	2025-06-03 09:53:47.143923	1
5590	187	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:47.232758	2025-06-03 09:53:47.232763	1
5591	188	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:47.321617	2025-06-03 09:53:47.321618	1
5592	181	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:47.74949	2025-06-03 09:53:47.749495	1
5593	179	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:47.838903	2025-06-03 09:53:47.838907	1
5594	178	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:47.92865	2025-06-03 09:53:47.928655	1
5595	180	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.019993	2025-06-03 09:53:48.019998	1
5596	182	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.113264	2025-06-03 09:53:48.113269	1
5597	175	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.202595	2025-06-03 09:53:48.202599	1
5598	173	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.29133	2025-06-03 09:53:48.291334	1
5599	172	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.381109	2025-06-03 09:53:48.381114	1
5600	171	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.47048	2025-06-03 09:53:48.470485	1
5601	174	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.559921	2025-06-03 09:53:48.559925	1
5602	177	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.649229	2025-06-03 09:53:48.649233	1
5603	169	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.73971	2025-06-03 09:53:48.739715	1
5604	183	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.829698	2025-06-03 09:53:48.829703	1
5605	226	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:48.918874	2025-06-03 09:53:48.918879	1
5606	227	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:49.00748	2025-06-03 09:53:49.007482	1
5607	193	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:49.481342	2025-06-03 09:53:49.481347	1
5608	191	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:49.57033	2025-06-03 09:53:49.570335	1
5609	189	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:49.65928	2025-06-03 09:53:49.659285	1
5610	190	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:49.748283	2025-06-03 09:53:49.748287	1
5611	192	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:49.838621	2025-06-03 09:53:49.838623	1
5612	194	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:50.239104	2025-06-03 09:53:50.239109	1
5613	195	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:50.33144	2025-06-03 09:53:50.331445	1
5614	196	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:50.420915	2025-06-03 09:53:50.420919	1
5615	197	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:50.510293	2025-06-03 09:53:50.510298	1
5616	200	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:50.59991	2025-06-03 09:53:50.599915	1
5617	202	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:50.689099	2025-06-03 09:53:50.689105	1
5618	203	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:50.779354	2025-06-03 09:53:50.779358	1
5619	205	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:50.868355	2025-06-03 09:53:50.86836	1
5620	206	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:50.958021	2025-06-03 09:53:50.958026	1
5621	207	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:51.047815	2025-06-03 09:53:51.04782	1
5622	208	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:51.138367	2025-06-03 09:53:51.138372	1
5623	209	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:51.228634	2025-06-03 09:53:51.228638	1
5624	198	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:51.31888	2025-06-03 09:53:51.318886	1
5625	201	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:51.408859	2025-06-03 09:53:51.408864	1
5626	204	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:51.498331	2025-06-03 09:53:51.498335	1
5627	214	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:51.587689	2025-06-03 09:53:51.587694	1
5628	225	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:51.678175	2025-06-03 09:53:51.67818	1
5629	230	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:51.767639	2025-06-03 09:53:51.767644	1
5630	231	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:51.856733	2025-06-03 09:53:51.856735	1
5631	216	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:52.256861	2025-06-03 09:53:52.256865	1
5632	217	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:52.345655	2025-06-03 09:53:52.34566	1
5633	218	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:52.43778	2025-06-03 09:53:52.437784	1
5634	219	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:52.529589	2025-06-03 09:53:52.529594	1
5635	220	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:52.61859	2025-06-03 09:53:52.618595	1
5636	221	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:52.70927	2025-06-03 09:53:52.709276	1
5637	222	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:52.799129	2025-06-03 09:53:52.799131	1
5638	223	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:53.197301	2025-06-03 09:53:53.197305	1
5639	224	2025-06-03	\N	\N	present	\N	2025-06-03 09:53:53.286679	2025-06-03 09:53:53.286681	1
5655	181	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:06.334182	2025-06-04 06:45:06.334187	1
5656	179	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:06.420844	2025-06-04 06:45:06.420848	1
5657	178	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:06.507324	2025-06-04 06:45:06.507329	1
5658	180	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:06.594349	2025-06-04 06:45:06.594354	1
5659	182	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:06.682611	2025-06-04 06:45:06.682615	1
5660	175	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:06.769247	2025-06-04 06:45:06.769251	1
5661	173	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:06.856554	2025-06-04 06:45:06.856558	1
5662	172	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:06.943297	2025-06-04 06:45:06.943301	1
5663	171	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:07.03259	2025-06-04 06:45:07.032594	1
5664	174	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:07.120003	2025-06-04 06:45:07.120032	1
5665	177	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:07.207086	2025-06-04 06:45:07.207099	1
5666	169	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:07.300929	2025-06-04 06:45:07.300933	1
5667	183	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:07.387978	2025-06-04 06:45:07.387983	1
5668	226	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:07.475449	2025-06-04 06:45:07.475453	1
5669	227	2025-06-04	\N	\N	present	\N	2025-06-04 06:45:07.56191	2025-06-04 06:45:07.561911	1
5670	184	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:03.448798	2025-06-09 19:06:03.448801	1
5671	185	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:03.543025	2025-06-09 19:06:03.543028	1
5672	186	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:03.620795	2025-06-09 19:06:03.620798	1
5673	187	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:03.69974	2025-06-09 19:06:03.699743	1
5674	188	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:03.777875	2025-06-09 19:06:03.777879	1
5675	184	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:03.857311	2025-06-09 19:06:03.857315	1
5676	185	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:03.935436	2025-06-09 19:06:03.93544	1
5677	186	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:04.014909	2025-06-09 19:06:04.014913	1
5678	187	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:04.09385	2025-06-09 19:06:04.093854	1
5679	188	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:04.171615	2025-06-09 19:06:04.17162	1
5680	184	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:04.250127	2025-06-09 19:06:04.250131	1
5681	185	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:04.334203	2025-06-09 19:06:04.334208	1
5682	186	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:04.412782	2025-06-09 19:06:04.412786	1
5683	187	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:04.494453	2025-06-09 19:06:04.494458	1
5684	188	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:04.572008	2025-06-09 19:06:04.572012	1
5685	184	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:04.649875	2025-06-09 19:06:04.649879	1
5686	185	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:04.74462	2025-06-09 19:06:04.744625	1
5687	186	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:04.822168	2025-06-09 19:06:04.822172	1
5688	187	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:04.900197	2025-06-09 19:06:04.900201	1
5689	188	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:04.978676	2025-06-09 19:06:04.97868	1
5690	184	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:05.057505	2025-06-09 19:06:05.057508	1
5691	185	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:05.135207	2025-06-09 19:06:05.135211	1
5692	186	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:05.213088	2025-06-09 19:06:05.213135	1
5693	187	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:05.293224	2025-06-09 19:06:05.293227	1
5694	188	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:05.371316	2025-06-09 19:06:05.37132	1
5695	184	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:05.454345	2025-06-09 19:06:05.45435	1
5696	185	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:05.532745	2025-06-09 19:06:05.532749	1
5697	186	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:05.610865	2025-06-09 19:06:05.610868	1
5698	187	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:05.688566	2025-06-09 19:06:05.688571	1
5699	188	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:05.7668	2025-06-09 19:06:05.766803	1
5700	179	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:08.58988	2025-06-09 19:06:08.589885	1
5701	178	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:08.668513	2025-06-09 19:06:08.668518	1
5702	180	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:08.748196	2025-06-09 19:06:08.7482	1
5703	182	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:08.82712	2025-06-09 19:06:08.827124	1
5704	175	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:08.905243	2025-06-09 19:06:08.905246	1
5705	173	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:08.983204	2025-06-09 19:06:08.983208	1
5706	172	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:09.066449	2025-06-09 19:06:09.066453	1
5707	171	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:09.167375	2025-06-09 19:06:09.167379	1
5708	174	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:09.245261	2025-06-09 19:06:09.245265	1
5709	177	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:09.323174	2025-06-09 19:06:09.323178	1
5710	169	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:09.400943	2025-06-09 19:06:09.400947	1
5711	183	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:09.481205	2025-06-09 19:06:09.481209	1
5712	181	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:09.559791	2025-06-09 19:06:09.559795	1
5713	226	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:09.637713	2025-06-09 19:06:09.637717	1
5714	227	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:09.794792	2025-06-09 19:06:09.794796	1
5715	179	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:09.879019	2025-06-09 19:06:09.879022	1
5716	178	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:09.956526	2025-06-09 19:06:09.956531	1
5717	180	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.034485	2025-06-09 19:06:10.034489	1
5718	182	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.112908	2025-06-09 19:06:10.112911	1
5719	175	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.190951	2025-06-09 19:06:10.190955	1
5720	173	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.269033	2025-06-09 19:06:10.269036	1
5721	172	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.346302	2025-06-09 19:06:10.346305	1
5722	171	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.423851	2025-06-09 19:06:10.423855	1
5723	174	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.502964	2025-06-09 19:06:10.502968	1
5724	177	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.593388	2025-06-09 19:06:10.593392	1
5725	169	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.676299	2025-06-09 19:06:10.676304	1
5726	183	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.754753	2025-06-09 19:06:10.754756	1
5727	181	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.832485	2025-06-09 19:06:10.832489	1
5728	226	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.912618	2025-06-09 19:06:10.912621	1
5729	227	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:10.99081	2025-06-09 19:06:10.990814	1
5730	179	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.070654	2025-06-09 19:06:11.070658	1
5731	178	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.149071	2025-06-09 19:06:11.149076	1
5732	180	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.227136	2025-06-09 19:06:11.22714	1
5733	182	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.305772	2025-06-09 19:06:11.305777	1
5734	175	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.383637	2025-06-09 19:06:11.383641	1
5735	173	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.46091	2025-06-09 19:06:11.460914	1
5736	172	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.539703	2025-06-09 19:06:11.539707	1
5737	171	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.618754	2025-06-09 19:06:11.618758	1
5738	174	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.724021	2025-06-09 19:06:11.724025	1
5739	177	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.803794	2025-06-09 19:06:11.803797	1
5740	169	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.881727	2025-06-09 19:06:11.881731	1
5741	183	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:11.959164	2025-06-09 19:06:11.959167	1
5742	181	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:12.036816	2025-06-09 19:06:12.03682	1
5743	226	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:12.119148	2025-06-09 19:06:12.119151	1
5744	227	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:12.197669	2025-06-09 19:06:12.197672	1
5745	179	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:12.276296	2025-06-09 19:06:12.276299	1
5746	178	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:12.354602	2025-06-09 19:06:12.354606	1
5747	180	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:12.436992	2025-06-09 19:06:12.436996	1
5748	182	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:12.515031	2025-06-09 19:06:12.515035	1
5749	175	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:12.593751	2025-06-09 19:06:12.593755	1
5750	173	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:12.67274	2025-06-09 19:06:12.672744	1
5751	172	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:12.75064	2025-06-09 19:06:12.750644	1
5752	171	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:12.828042	2025-06-09 19:06:12.828046	1
5753	174	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:12.917887	2025-06-09 19:06:12.917891	1
5754	177	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:12.995435	2025-06-09 19:06:12.99544	1
5755	169	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:13.07322	2025-06-09 19:06:13.073224	1
5756	183	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:13.150616	2025-06-09 19:06:13.15062	1
5757	181	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:13.228464	2025-06-09 19:06:13.228467	1
5758	226	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:13.305854	2025-06-09 19:06:13.305857	1
5759	227	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:13.383632	2025-06-09 19:06:13.383635	1
5760	179	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:13.461192	2025-06-09 19:06:13.461196	1
5761	178	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:13.539036	2025-06-09 19:06:13.53904	1
5762	180	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:13.61659	2025-06-09 19:06:13.616595	1
5763	182	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:13.694702	2025-06-09 19:06:13.694706	1
5764	175	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:13.772621	2025-06-09 19:06:13.772625	1
5765	173	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:13.850122	2025-06-09 19:06:13.850126	1
5766	172	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:13.928016	2025-06-09 19:06:13.92802	1
5767	171	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:14.005835	2025-06-09 19:06:14.005839	1
5768	174	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:14.083692	2025-06-09 19:06:14.083695	1
5769	177	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:14.161477	2025-06-09 19:06:14.161481	1
5770	169	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:14.239647	2025-06-09 19:06:14.23965	1
5771	183	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:14.317822	2025-06-09 19:06:14.317825	1
5772	181	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:14.395281	2025-06-09 19:06:14.395284	1
5773	226	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:14.472743	2025-06-09 19:06:14.472746	1
5774	227	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:14.552559	2025-06-09 19:06:14.552563	1
5775	193	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:15.591282	2025-06-09 19:06:15.591287	1
5776	191	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:15.669856	2025-06-09 19:06:15.669859	1
5777	189	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:15.749864	2025-06-09 19:06:15.749868	1
5778	190	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:15.827615	2025-06-09 19:06:15.827619	1
5779	192	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:15.906566	2025-06-09 19:06:15.90657	1
5780	193	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:15.986216	2025-06-09 19:06:15.98622	1
5781	191	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:16.064397	2025-06-09 19:06:16.064401	1
5782	189	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:16.142082	2025-06-09 19:06:16.142085	1
5783	190	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:16.219656	2025-06-09 19:06:16.219659	1
5784	192	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:16.298258	2025-06-09 19:06:16.298262	1
5785	193	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:16.376117	2025-06-09 19:06:16.376121	1
5786	191	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:16.455507	2025-06-09 19:06:16.455511	1
5787	189	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:16.533217	2025-06-09 19:06:16.533221	1
5788	190	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:16.611914	2025-06-09 19:06:16.611917	1
5789	192	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:16.692128	2025-06-09 19:06:16.692132	1
5790	193	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:16.771653	2025-06-09 19:06:16.771658	1
5791	191	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:16.849901	2025-06-09 19:06:16.849906	1
5792	189	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:16.929274	2025-06-09 19:06:16.929278	1
5793	190	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:17.007676	2025-06-09 19:06:17.00768	1
5794	192	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:17.094288	2025-06-09 19:06:17.094292	1
5795	193	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:17.207939	2025-06-09 19:06:17.207942	1
5796	191	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:17.328685	2025-06-09 19:06:17.328689	1
5797	189	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:17.437124	2025-06-09 19:06:17.437128	1
5798	190	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:17.542531	2025-06-09 19:06:17.542535	1
5799	192	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:17.622282	2025-06-09 19:06:17.622286	1
5800	193	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:17.702259	2025-06-09 19:06:17.702263	1
5801	191	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:17.782216	2025-06-09 19:06:17.78222	1
5802	189	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:17.890238	2025-06-09 19:06:17.890242	1
5803	190	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:17.969462	2025-06-09 19:06:17.969466	1
5804	192	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:18.061329	2025-06-09 19:06:18.061332	1
5805	194	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:20.768854	2025-06-09 19:06:20.768858	1
5806	195	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:20.846546	2025-06-09 19:06:20.846549	1
5807	196	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:20.92407	2025-06-09 19:06:20.924074	1
5808	197	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.001794	2025-06-09 19:06:21.001798	1
5809	200	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.081005	2025-06-09 19:06:21.081008	1
5810	202	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.159528	2025-06-09 19:06:21.159532	1
5811	203	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.238202	2025-06-09 19:06:21.238206	1
5812	205	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.31606	2025-06-09 19:06:21.316063	1
5813	206	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.393874	2025-06-09 19:06:21.393878	1
5814	207	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.471919	2025-06-09 19:06:21.471922	1
5815	208	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.549791	2025-06-09 19:06:21.549795	1
5816	209	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.632712	2025-06-09 19:06:21.632715	1
5817	198	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.711962	2025-06-09 19:06:21.711966	1
5818	201	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.789652	2025-06-09 19:06:21.789655	1
5819	204	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.867165	2025-06-09 19:06:21.867168	1
5820	214	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:21.946259	2025-06-09 19:06:21.946264	1
5821	225	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:22.025415	2025-06-09 19:06:22.025419	1
5822	230	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:22.111063	2025-06-09 19:06:22.111068	1
5823	231	2025-06-04	\N	\N	present	\N	2025-06-09 19:06:22.188882	2025-06-09 19:06:22.188886	1
5824	194	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:22.266769	2025-06-09 19:06:22.266773	1
5825	195	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:22.345355	2025-06-09 19:06:22.34536	1
5826	196	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:22.42394	2025-06-09 19:06:22.423944	1
5827	197	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:22.508417	2025-06-09 19:06:22.508427	1
5828	200	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:22.586326	2025-06-09 19:06:22.586331	1
5829	202	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:22.664804	2025-06-09 19:06:22.664809	1
5830	203	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:22.753249	2025-06-09 19:06:22.753252	1
5831	205	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:22.83408	2025-06-09 19:06:22.834085	1
5832	206	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:22.919331	2025-06-09 19:06:22.919336	1
5833	207	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:22.996687	2025-06-09 19:06:22.996691	1
5834	208	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:23.073892	2025-06-09 19:06:23.073895	1
5835	209	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:23.152586	2025-06-09 19:06:23.152588	1
5836	198	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:23.236867	2025-06-09 19:06:23.236869	1
5837	201	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:23.31524	2025-06-09 19:06:23.315244	1
5838	204	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:23.397595	2025-06-09 19:06:23.397599	1
5839	214	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:23.476737	2025-06-09 19:06:23.47674	1
5840	225	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:23.55476	2025-06-09 19:06:23.554763	1
5841	230	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:23.63216	2025-06-09 19:06:23.632164	1
5842	231	2025-06-05	\N	\N	present	\N	2025-06-09 19:06:23.709915	2025-06-09 19:06:23.709918	1
5843	194	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:23.789979	2025-06-09 19:06:23.789982	1
5844	195	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:23.86778	2025-06-09 19:06:23.867783	1
5845	196	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:23.945606	2025-06-09 19:06:23.945609	1
5846	197	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.023455	2025-06-09 19:06:24.02346	1
5847	200	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.102167	2025-06-09 19:06:24.102177	1
5848	202	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.180971	2025-06-09 19:06:24.180974	1
5849	203	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.263256	2025-06-09 19:06:24.263261	1
5850	205	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.342852	2025-06-09 19:06:24.342856	1
5851	206	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.428258	2025-06-09 19:06:24.428262	1
5852	207	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.506578	2025-06-09 19:06:24.506581	1
5853	208	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.584266	2025-06-09 19:06:24.584271	1
5854	209	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.663733	2025-06-09 19:06:24.663737	1
5855	198	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.741696	2025-06-09 19:06:24.7417	1
5856	201	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.819028	2025-06-09 19:06:24.819032	1
5857	204	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.897522	2025-06-09 19:06:24.897526	1
5858	214	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:24.975211	2025-06-09 19:06:24.975215	1
5859	225	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:25.057393	2025-06-09 19:06:25.057397	1
5860	230	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:25.136276	2025-06-09 19:06:25.136279	1
5861	231	2025-06-06	\N	\N	present	\N	2025-06-09 19:06:25.214876	2025-06-09 19:06:25.21488	1
5862	194	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:25.293017	2025-06-09 19:06:25.293021	1
5863	195	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:25.376573	2025-06-09 19:06:25.376576	1
5864	196	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:25.456874	2025-06-09 19:06:25.456878	1
5865	197	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:25.534507	2025-06-09 19:06:25.53451	1
5866	200	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:25.612769	2025-06-09 19:06:25.612772	1
5867	202	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:25.692367	2025-06-09 19:06:25.692372	1
5868	203	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:25.771532	2025-06-09 19:06:25.771536	1
5869	205	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:25.849501	2025-06-09 19:06:25.849505	1
5870	206	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:25.927613	2025-06-09 19:06:25.927618	1
5871	207	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:26.005956	2025-06-09 19:06:26.00596	1
5872	208	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:26.085485	2025-06-09 19:06:26.085489	1
5873	209	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:26.164642	2025-06-09 19:06:26.164645	1
5874	198	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:26.24316	2025-06-09 19:06:26.243164	1
5875	201	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:26.32279	2025-06-09 19:06:26.322794	1
5876	204	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:26.401653	2025-06-09 19:06:26.401657	1
5877	214	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:26.481774	2025-06-09 19:06:26.481778	1
5878	225	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:26.560354	2025-06-09 19:06:26.560358	1
5879	230	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:26.639245	2025-06-09 19:06:26.63925	1
5880	231	2025-06-07	\N	\N	present	\N	2025-06-09 19:06:26.718127	2025-06-09 19:06:26.718132	1
5881	194	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:26.795994	2025-06-09 19:06:26.795998	1
5882	195	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:26.876668	2025-06-09 19:06:26.876672	1
5883	196	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:26.954279	2025-06-09 19:06:26.954283	1
5884	197	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.033328	2025-06-09 19:06:27.033332	1
5885	200	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.111086	2025-06-09 19:06:27.111107	1
5886	202	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.189557	2025-06-09 19:06:27.18956	1
5887	203	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.268178	2025-06-09 19:06:27.268182	1
5888	205	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.345962	2025-06-09 19:06:27.345966	1
5889	206	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.423499	2025-06-09 19:06:27.423503	1
5890	207	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.501829	2025-06-09 19:06:27.501832	1
5891	208	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.579987	2025-06-09 19:06:27.579992	1
5892	209	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.659565	2025-06-09 19:06:27.659569	1
5893	198	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.7388	2025-06-09 19:06:27.738804	1
5894	201	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.818205	2025-06-09 19:06:27.818209	1
5895	204	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.898312	2025-06-09 19:06:27.898315	1
5896	214	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:27.976716	2025-06-09 19:06:27.97672	1
5897	225	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:28.054682	2025-06-09 19:06:28.054686	1
5898	230	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:28.133415	2025-06-09 19:06:28.133423	1
5899	231	2025-06-08	\N	\N	present	\N	2025-06-09 19:06:28.213268	2025-06-09 19:06:28.213272	1
5900	194	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:28.291725	2025-06-09 19:06:28.291729	1
5901	195	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:28.369741	2025-06-09 19:06:28.369746	1
5902	196	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:28.44734	2025-06-09 19:06:28.447344	1
5903	197	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:28.524736	2025-06-09 19:06:28.524739	1
5904	200	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:28.602168	2025-06-09 19:06:28.602171	1
5905	202	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:28.680482	2025-06-09 19:06:28.680485	1
5906	203	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:28.758231	2025-06-09 19:06:28.758236	1
5907	205	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:28.83948	2025-06-09 19:06:28.839485	1
5908	206	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:28.917548	2025-06-09 19:06:28.917552	1
5909	207	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:28.994707	2025-06-09 19:06:28.99471	1
5910	208	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:29.073033	2025-06-09 19:06:29.073037	1
5911	209	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:29.151328	2025-06-09 19:06:29.151333	1
5912	198	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:29.229496	2025-06-09 19:06:29.229499	1
5913	201	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:29.307206	2025-06-09 19:06:29.307209	1
5914	204	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:29.384931	2025-06-09 19:06:29.384934	1
5915	214	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:29.463314	2025-06-09 19:06:29.463317	1
5916	225	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:29.541071	2025-06-09 19:06:29.541075	1
5917	230	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:29.618746	2025-06-09 19:06:29.61875	1
5918	231	2025-06-09	\N	\N	present	\N	2025-06-09 19:06:29.69691	2025-06-09 19:06:29.696913	1
5951	216	2025-06-04	\N	\N	present	\N	2025-06-09 19:07:07.796041	2025-06-09 19:07:07.796044	1
5952	217	2025-06-04	\N	\N	present	\N	2025-06-09 19:07:07.883953	2025-06-09 19:07:07.883958	1
5953	218	2025-06-04	\N	\N	present	\N	2025-06-09 19:07:07.972591	2025-06-09 19:07:07.972595	1
5954	219	2025-06-04	\N	\N	present	\N	2025-06-09 19:07:08.06104	2025-06-09 19:07:08.061045	1
5955	220	2025-06-04	\N	\N	present	\N	2025-06-09 19:07:08.14864	2025-06-09 19:07:08.148644	1
5956	221	2025-06-04	\N	\N	present	\N	2025-06-09 19:07:08.235674	2025-06-09 19:07:08.235677	1
5957	222	2025-06-04	\N	\N	present	\N	2025-06-09 19:07:08.326588	2025-06-09 19:07:08.326592	1
5958	216	2025-06-05	\N	\N	present	\N	2025-06-09 19:07:08.413499	2025-06-09 19:07:08.413502	1
5959	217	2025-06-05	\N	\N	present	\N	2025-06-09 19:07:08.503164	2025-06-09 19:07:08.503168	1
5960	218	2025-06-05	\N	\N	present	\N	2025-06-09 19:07:08.590594	2025-06-09 19:07:08.590598	1
5961	219	2025-06-05	\N	\N	present	\N	2025-06-09 19:07:08.677883	2025-06-09 19:07:08.677887	1
5962	220	2025-06-05	\N	\N	present	\N	2025-06-09 19:07:08.767472	2025-06-09 19:07:08.767476	1
5963	221	2025-06-05	\N	\N	present	\N	2025-06-09 19:07:08.856696	2025-06-09 19:07:08.8567	1
5964	222	2025-06-05	\N	\N	present	\N	2025-06-09 19:07:08.944769	2025-06-09 19:07:08.944772	1
5965	216	2025-06-06	\N	\N	present	\N	2025-06-09 19:07:09.032028	2025-06-09 19:07:09.032032	1
5966	217	2025-06-06	\N	\N	present	\N	2025-06-09 19:07:09.119456	2025-06-09 19:07:09.11946	1
5967	218	2025-06-06	\N	\N	present	\N	2025-06-09 19:07:09.209181	2025-06-09 19:07:09.209185	1
5968	219	2025-06-06	\N	\N	present	\N	2025-06-09 19:07:09.296668	2025-06-09 19:07:09.296672	1
5969	220	2025-06-06	\N	\N	present	\N	2025-06-09 19:07:09.383976	2025-06-09 19:07:09.383979	1
5970	221	2025-06-06	\N	\N	present	\N	2025-06-09 19:07:09.471921	2025-06-09 19:07:09.471926	1
5971	222	2025-06-06	\N	\N	present	\N	2025-06-09 19:07:09.559785	2025-06-09 19:07:09.559789	1
5972	216	2025-06-07	\N	\N	present	\N	2025-06-09 19:07:09.649753	2025-06-09 19:07:09.649758	1
5973	217	2025-06-07	\N	\N	present	\N	2025-06-09 19:07:09.736768	2025-06-09 19:07:09.736771	1
5974	218	2025-06-07	\N	\N	present	\N	2025-06-09 19:07:09.824579	2025-06-09 19:07:09.824583	1
5975	219	2025-06-07	\N	\N	present	\N	2025-06-09 19:07:09.91193	2025-06-09 19:07:09.911934	1
5976	220	2025-06-07	\N	\N	present	\N	2025-06-09 19:07:09.999306	2025-06-09 19:07:09.99931	1
5977	221	2025-06-07	\N	\N	present	\N	2025-06-09 19:07:10.086793	2025-06-09 19:07:10.086796	1
5978	222	2025-06-07	\N	\N	present	\N	2025-06-09 19:07:10.174479	2025-06-09 19:07:10.174483	1
5979	216	2025-06-08	\N	\N	present	\N	2025-06-09 19:07:10.262528	2025-06-09 19:07:10.262532	1
5980	217	2025-06-08	\N	\N	present	\N	2025-06-09 19:07:10.34956	2025-06-09 19:07:10.349564	1
5981	218	2025-06-08	\N	\N	present	\N	2025-06-09 19:07:10.437796	2025-06-09 19:07:10.437799	1
5982	219	2025-06-08	\N	\N	present	\N	2025-06-09 19:07:10.525312	2025-06-09 19:07:10.525316	1
5983	220	2025-06-08	\N	\N	present	\N	2025-06-09 19:07:10.612829	2025-06-09 19:07:10.612833	1
5984	221	2025-06-08	\N	\N	present	\N	2025-06-09 19:07:10.70692	2025-06-09 19:07:10.706925	1
5985	222	2025-06-08	\N	\N	present	\N	2025-06-09 19:07:10.79377	2025-06-09 19:07:10.793774	1
5986	216	2025-06-09	\N	\N	present	\N	2025-06-09 19:07:10.880768	2025-06-09 19:07:10.880771	1
5987	217	2025-06-09	\N	\N	present	\N	2025-06-09 19:07:10.968547	2025-06-09 19:07:10.968551	1
5988	218	2025-06-09	\N	\N	present	\N	2025-06-09 19:07:11.056124	2025-06-09 19:07:11.056128	1
5989	219	2025-06-09	\N	\N	present	\N	2025-06-09 19:07:11.143145	2025-06-09 19:07:11.14315	1
5990	220	2025-06-09	\N	\N	present	\N	2025-06-09 19:07:11.230931	2025-06-09 19:07:11.230936	1
5991	221	2025-06-09	\N	\N	present	\N	2025-06-09 19:07:11.318799	2025-06-09 19:07:11.318804	1
5992	222	2025-06-09	\N	\N	present	\N	2025-06-09 19:07:11.406644	2025-06-09 19:07:11.406647	1
5993	223	2025-06-04	\N	\N	present	\N	2025-06-09 19:07:12.156231	2025-06-09 19:07:12.156234	1
5994	224	2025-06-04	\N	\N	present	\N	2025-06-09 19:07:12.244171	2025-06-09 19:07:12.244176	1
5995	223	2025-06-05	\N	\N	present	\N	2025-06-09 19:07:12.331176	2025-06-09 19:07:12.331179	1
5996	224	2025-06-05	\N	\N	present	\N	2025-06-09 19:07:12.418584	2025-06-09 19:07:12.418588	1
5997	223	2025-06-06	\N	\N	present	\N	2025-06-09 19:07:12.507155	2025-06-09 19:07:12.507159	1
5998	224	2025-06-06	\N	\N	present	\N	2025-06-09 19:07:12.595327	2025-06-09 19:07:12.595331	1
5999	223	2025-06-07	\N	\N	present	\N	2025-06-09 19:07:12.682306	2025-06-09 19:07:12.682309	1
6000	224	2025-06-07	\N	\N	present	\N	2025-06-09 19:07:12.77207	2025-06-09 19:07:12.772074	1
6001	223	2025-06-08	\N	\N	present	\N	2025-06-09 19:07:12.859673	2025-06-09 19:07:12.859677	1
6002	224	2025-06-08	\N	\N	present	\N	2025-06-09 19:07:12.946587	2025-06-09 19:07:12.946591	1
6003	223	2025-06-09	\N	\N	present	\N	2025-06-09 19:07:13.033562	2025-06-09 19:07:13.033566	1
6004	224	2025-06-09	\N	\N	present	\N	2025-06-09 19:07:13.120463	2025-06-09 19:07:13.120466	1
6287	184	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:32.792753	2025-06-11 13:35:32.792757	1
6288	185	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:32.909144	2025-06-11 13:35:32.90915	1
6289	186	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:33.000435	2025-06-11 13:35:33.000439	1
6290	187	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:33.092604	2025-06-11 13:35:33.092609	1
6291	188	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:33.184493	2025-06-11 13:35:33.184497	1
6292	184	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:33.276306	2025-06-11 13:35:33.27631	1
6293	185	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:33.368022	2025-06-11 13:35:33.368028	1
6294	186	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:33.459828	2025-06-11 13:35:33.459833	1
6295	187	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:33.551207	2025-06-11 13:35:33.551212	1
6296	188	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:33.642668	2025-06-11 13:35:33.64267	1
6297	178	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:40.388682	2025-06-11 13:35:40.388687	1
6298	180	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:40.48101	2025-06-11 13:35:40.481015	1
6299	182	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:40.576475	2025-06-11 13:35:40.576479	1
6300	175	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:40.669115	2025-06-11 13:35:40.669119	1
6301	173	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:40.76236	2025-06-11 13:35:40.762365	1
6302	172	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:40.854081	2025-06-11 13:35:40.854086	1
6303	171	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:40.947115	2025-06-11 13:35:40.947119	1
6304	174	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:41.039334	2025-06-11 13:35:41.039339	1
6305	177	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:41.1312	2025-06-11 13:35:41.131205	1
6306	169	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:41.224587	2025-06-11 13:35:41.224612	1
6307	183	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:41.316655	2025-06-11 13:35:41.31666	1
6308	181	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:41.410736	2025-06-11 13:35:41.410741	1
6309	179	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:41.503834	2025-06-11 13:35:41.503839	1
6310	226	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:41.595767	2025-06-11 13:35:41.595772	1
6311	227	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:41.724364	2025-06-11 13:35:41.724368	1
6312	178	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:41.8158	2025-06-11 13:35:41.815804	1
6313	180	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:41.907548	2025-06-11 13:35:41.907553	1
6314	182	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:41.999481	2025-06-11 13:35:41.999485	1
6315	175	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:42.091315	2025-06-11 13:35:42.09132	1
6316	173	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:42.182976	2025-06-11 13:35:42.182981	1
6317	172	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:42.274527	2025-06-11 13:35:42.274532	1
6318	171	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:42.371119	2025-06-11 13:35:42.371124	1
6345	206	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:55.81515	2025-06-11 13:35:55.815154	1
6346	207	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:55.912011	2025-06-11 13:35:55.912016	1
6347	208	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:56.00346	2025-06-11 13:35:56.003465	1
6349	198	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:56.186211	2025-06-11 13:35:56.186216	1
6350	201	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:56.277958	2025-06-11 13:35:56.277962	1
6351	204	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:56.370848	2025-06-11 13:35:56.370853	1
6352	214	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:56.473326	2025-06-11 13:35:56.473332	1
6353	225	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:56.565954	2025-06-11 13:35:56.565958	1
6354	230	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:56.657734	2025-06-11 13:35:56.657738	1
6355	231	2025-06-10	\N	\N	present	\N	2025-06-11 13:35:56.750115	2025-06-11 13:35:56.750119	1
6356	194	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:56.841986	2025-06-11 13:35:56.84199	1
6357	195	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:56.933739	2025-06-11 13:35:56.933744	1
6358	196	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.027606	2025-06-11 13:35:57.02761	1
6359	197	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.119204	2025-06-11 13:35:57.119209	1
6360	200	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.210607	2025-06-11 13:35:57.210611	1
6361	202	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.301974	2025-06-11 13:35:57.301978	1
6362	203	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.398187	2025-06-11 13:35:57.398191	1
6363	205	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.49047	2025-06-11 13:35:57.490474	1
6364	206	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.582545	2025-06-11 13:35:57.58255	1
6365	207	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.674568	2025-06-11 13:35:57.674572	1
6366	208	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.766594	2025-06-11 13:35:57.766598	1
6367	209	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.860044	2025-06-11 13:35:57.860049	1
6368	198	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:57.952336	2025-06-11 13:35:57.95234	1
6369	201	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:58.047771	2025-06-11 13:35:58.047776	1
6370	204	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:58.140125	2025-06-11 13:35:58.140129	1
6371	214	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:58.231395	2025-06-11 13:35:58.2314	1
6372	225	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:58.322816	2025-06-11 13:35:58.322821	1
6373	230	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:58.416071	2025-06-11 13:35:58.416076	1
6374	231	2025-06-11	\N	\N	present	\N	2025-06-11 13:35:58.513338	2025-06-11 13:35:58.513341	1
6375	216	2025-06-10	\N	\N	present	\N	2025-06-11 13:36:37.214292	2025-06-11 13:36:37.214297	1
6376	217	2025-06-10	\N	\N	present	\N	2025-06-11 13:36:37.306289	2025-06-11 13:36:37.306293	1
6377	218	2025-06-10	\N	\N	present	\N	2025-06-11 13:36:37.396321	2025-06-11 13:36:37.396326	1
6378	219	2025-06-10	\N	\N	present	\N	2025-06-11 13:36:37.488507	2025-06-11 13:36:37.488511	1
6379	220	2025-06-10	\N	\N	present	\N	2025-06-11 13:36:37.578982	2025-06-11 13:36:37.578987	1
6380	221	2025-06-10	\N	\N	present	\N	2025-06-11 13:36:37.66955	2025-06-11 13:36:37.669554	1
6381	222	2025-06-10	\N	\N	present	\N	2025-06-11 13:36:37.76044	2025-06-11 13:36:37.760444	1
6382	216	2025-06-11	\N	\N	present	\N	2025-06-11 13:36:37.851107	2025-06-11 13:36:37.851112	1
6383	217	2025-06-11	\N	\N	present	\N	2025-06-11 13:36:37.944502	2025-06-11 13:36:37.944507	1
6384	218	2025-06-11	\N	\N	present	\N	2025-06-11 13:36:38.034486	2025-06-11 13:36:38.03449	1
6385	219	2025-06-11	\N	\N	present	\N	2025-06-11 13:36:38.125512	2025-06-11 13:36:38.125516	1
6386	220	2025-06-11	\N	\N	present	\N	2025-06-11 13:36:38.216541	2025-06-11 13:36:38.216545	1
6387	221	2025-06-11	\N	\N	present	\N	2025-06-11 13:36:38.308903	2025-06-11 13:36:38.308907	1
6388	222	2025-06-11	\N	\N	present	\N	2025-06-11 13:36:38.400536	2025-06-11 13:36:38.400537	1
6389	223	2025-06-10	\N	\N	present	\N	2025-06-11 13:36:39.642366	2025-06-11 13:36:39.642371	1
6390	224	2025-06-10	\N	\N	present	\N	2025-06-11 13:36:39.732923	2025-06-11 13:36:39.732927	1
6391	223	2025-06-11	\N	\N	present	\N	2025-06-11 13:36:39.823925	2025-06-11 13:36:39.82393	1
6392	224	2025-06-11	\N	\N	present	\N	2025-06-11 13:36:39.914172	2025-06-11 13:36:39.914173	1
6348	209	2025-06-10	\N	\N	absent	غياب بسبب عدم الالتزام والانتظام بي العمل 	2025-06-11 13:35:56.094887	2025-06-11 13:57:35.227292	1
6324	179	2025-06-11	14:27:28.586181	\N	حاضر	\N	2025-06-11 13:35:42.9294	2025-06-11 14:27:28.588065	1
6393	182	2025-06-12	\N	\N	leave	اخد اجازه  تاريخ 12وراح يداوم الجمعه	2025-06-12 13:10:59.804773	2025-06-12 13:10:59.804777	1
6446	174	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:09.475081	2025-06-12 15:30:09.475086	1
6447	216	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:09.569548	2025-06-12 15:30:09.569553	1
6448	193	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:09.662703	2025-06-12 15:30:09.662707	1
6449	214	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:09.75563	2025-06-12 15:30:09.755635	1
6450	205	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:09.848423	2025-06-12 15:30:09.848427	1
6451	224	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:09.94186	2025-06-12 15:30:09.941865	1
6452	198	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:10.04091	2025-06-12 15:30:10.040914	1
6453	191	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:10.134405	2025-06-12 15:30:10.13441	1
6454	190	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:10.228974	2025-06-12 15:30:10.228978	1
6455	180	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:10.326771	2025-06-12 15:30:10.326776	1
6456	200	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:10.422278	2025-06-12 15:30:10.422282	1
6457	217	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:10.531676	2025-06-12 15:30:10.531682	1
6458	218	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:10.62521	2025-06-12 15:30:10.625215	1
6459	197	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:10.720866	2025-06-12 15:30:10.720871	1
6460	219	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:10.815401	2025-06-12 15:30:10.815406	1
6461	209	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:10.911275	2025-06-12 15:30:10.91128	1
6462	184	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.005269	2025-06-12 15:30:11.005274	1
6463	188	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.099293	2025-06-12 15:30:11.099297	1
6464	221	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.192704	2025-06-12 15:30:11.192709	1
6465	208	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.288734	2025-06-12 15:30:11.288739	1
6466	207	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.384022	2025-06-12 15:30:11.384027	1
6467	232	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.478649	2025-06-12 15:30:11.478654	1
6468	220	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.572788	2025-06-12 15:30:11.572793	1
6469	189	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.668156	2025-06-12 15:30:11.668161	1
6470	227	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.761994	2025-06-12 15:30:11.761998	1
6471	176	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.855195	2025-06-12 15:30:11.855199	1
6472	195	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:11.948506	2025-06-12 15:30:11.948511	1
6473	226	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:12.042422	2025-06-12 15:30:12.042426	1
6474	173	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:12.136634	2025-06-12 15:30:12.136638	1
6475	175	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:12.237635	2025-06-12 15:30:12.23764	1
6476	201	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:12.3367	2025-06-12 15:30:12.336704	1
6477	202	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:12.430545	2025-06-12 15:30:12.43055	1
6478	225	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:12.575572	2025-06-12 15:30:12.575577	1
6479	206	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:12.671403	2025-06-12 15:30:12.671408	1
6480	192	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:12.766428	2025-06-12 15:30:12.766432	1
6481	185	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:12.860098	2025-06-12 15:30:12.860103	1
6482	204	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:12.953644	2025-06-12 15:30:12.953649	1
6483	179	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.048086	2025-06-12 15:30:13.048091	1
6484	222	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.141247	2025-06-12 15:30:13.141251	1
6485	230	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.237442	2025-06-12 15:30:13.237447	1
6486	194	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.331344	2025-06-12 15:30:13.331349	1
6487	231	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.426055	2025-06-12 15:30:13.42606	1
6488	181	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.521821	2025-06-12 15:30:13.521826	1
6489	203	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.62086	2025-06-12 15:30:13.620865	1
6490	196	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.714282	2025-06-12 15:30:13.714287	1
6491	178	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.807655	2025-06-12 15:30:13.80766	1
6492	187	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.902479	2025-06-12 15:30:13.902484	1
6493	186	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:13.995852	2025-06-12 15:30:13.995857	1
6494	177	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:14.090276	2025-06-12 15:30:14.090281	1
6495	171	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:14.184355	2025-06-12 15:30:14.18436	1
6496	223	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:14.279242	2025-06-12 15:30:14.279246	1
6497	172	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:14.372745	2025-06-12 15:30:14.37275	1
6498	183	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:14.467035	2025-06-12 15:30:14.467039	1
6499	169	2025-06-12	\N	\N	present	\N	2025-06-12 15:30:14.560483	2025-06-12 15:30:14.560488	1
6500	226	2025-06-13	\N	\N	present		2025-06-14 05:44:27.842974	2025-06-14 05:44:27.842979	1
6501	177	2025-06-13	\N	\N	present		2025-06-14 05:45:04.927729	2025-06-14 05:45:04.927735	1
6502	169	2025-06-13	\N	\N	present		2025-06-14 05:47:01.667268	2025-06-14 05:47:01.667272	1
6541	184	2025-06-13	\N	\N	present	\N	2025-06-14 19:37:59.680347	2025-06-14 19:37:59.680352	1
6542	185	2025-06-13	\N	\N	present	\N	2025-06-14 19:37:59.768379	2025-06-14 19:37:59.768383	1
6543	186	2025-06-13	\N	\N	present	\N	2025-06-14 19:37:59.85691	2025-06-14 19:37:59.856914	1
6544	187	2025-06-13	\N	\N	present	\N	2025-06-14 19:37:59.944406	2025-06-14 19:37:59.94441	1
6545	188	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:00.03269	2025-06-14 19:38:00.032694	1
6546	184	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:00.121278	2025-06-14 19:38:00.121283	1
6547	185	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:00.209332	2025-06-14 19:38:00.209337	1
6548	186	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:00.297493	2025-06-14 19:38:00.297497	1
6549	187	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:00.385585	2025-06-14 19:38:00.38559	1
6550	188	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:00.476056	2025-06-14 19:38:00.476057	1
6551	193	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:00.886416	2025-06-14 19:38:00.886421	1
6552	191	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:00.975033	2025-06-14 19:38:00.975037	1
6553	189	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:01.064737	2025-06-14 19:38:01.064741	1
6554	190	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:01.155214	2025-06-14 19:38:01.155219	1
6555	192	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:01.245533	2025-06-14 19:38:01.245537	1
6556	193	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:01.334378	2025-06-14 19:38:01.334382	1
6557	191	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:01.422829	2025-06-14 19:38:01.422834	1
6558	189	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:01.511961	2025-06-14 19:38:01.511965	1
6559	190	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:01.60039	2025-06-14 19:38:01.600395	1
6560	192	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:01.692085	2025-06-14 19:38:01.692087	1
6561	194	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.086881	2025-06-14 19:38:02.086885	1
6562	195	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.176914	2025-06-14 19:38:02.176918	1
6563	196	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.264947	2025-06-14 19:38:02.264952	1
6564	197	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.353908	2025-06-14 19:38:02.353912	1
6565	200	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.442005	2025-06-14 19:38:02.442009	1
6566	202	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.531717	2025-06-14 19:38:02.531722	1
6567	203	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.620765	2025-06-14 19:38:02.62077	1
6568	205	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.710235	2025-06-14 19:38:02.71024	1
6569	206	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.798539	2025-06-14 19:38:02.798544	1
6570	207	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.887004	2025-06-14 19:38:02.887009	1
6571	208	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:02.975533	2025-06-14 19:38:02.975538	1
6572	209	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:03.064182	2025-06-14 19:38:03.064187	1
6573	198	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:03.153062	2025-06-14 19:38:03.153068	1
6574	201	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:03.241284	2025-06-14 19:38:03.241288	1
6575	204	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:03.330178	2025-06-14 19:38:03.330183	1
6576	214	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:03.420085	2025-06-14 19:38:03.42009	1
6577	225	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:03.509008	2025-06-14 19:38:03.509012	1
6578	230	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:03.597134	2025-06-14 19:38:03.597139	1
6579	231	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:03.68537	2025-06-14 19:38:03.685374	1
6580	194	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:03.774351	2025-06-14 19:38:03.774355	1
6581	195	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:03.862778	2025-06-14 19:38:03.862783	1
6582	196	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:03.951434	2025-06-14 19:38:03.951439	1
6583	197	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.039518	2025-06-14 19:38:04.039523	1
6584	200	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.128863	2025-06-14 19:38:04.128868	1
6585	202	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.221434	2025-06-14 19:38:04.221438	1
6586	203	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.31153	2025-06-14 19:38:04.311535	1
6587	205	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.401534	2025-06-14 19:38:04.401538	1
6588	206	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.490031	2025-06-14 19:38:04.490036	1
6589	207	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.578851	2025-06-14 19:38:04.578856	1
6590	208	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.66799	2025-06-14 19:38:04.667995	1
6591	209	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.757091	2025-06-14 19:38:04.757095	1
6592	198	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.846488	2025-06-14 19:38:04.846493	1
6593	201	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:04.935959	2025-06-14 19:38:04.935964	1
6594	204	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:05.02739	2025-06-14 19:38:05.027394	1
6595	214	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:05.117214	2025-06-14 19:38:05.117219	1
6596	225	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:05.207375	2025-06-14 19:38:05.207379	1
6597	230	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:05.296231	2025-06-14 19:38:05.296236	1
6598	231	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:05.384555	2025-06-14 19:38:05.384556	1
6599	216	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:05.782506	2025-06-14 19:38:05.782511	1
6600	217	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:05.875251	2025-06-14 19:38:05.875255	1
6601	218	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:05.964699	2025-06-14 19:38:05.964704	1
6602	219	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:06.053228	2025-06-14 19:38:06.053233	1
6603	220	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:06.142619	2025-06-14 19:38:06.142624	1
6604	221	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:06.231331	2025-06-14 19:38:06.231336	1
6605	222	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:06.32023	2025-06-14 19:38:06.320234	1
6606	216	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:06.408827	2025-06-14 19:38:06.408832	1
6607	217	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:06.497977	2025-06-14 19:38:06.497981	1
6608	218	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:06.586449	2025-06-14 19:38:06.586453	1
6609	219	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:06.67491	2025-06-14 19:38:06.674914	1
6610	220	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:06.763618	2025-06-14 19:38:06.763623	1
6611	221	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:06.852259	2025-06-14 19:38:06.852264	1
6612	222	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:06.940815	2025-06-14 19:38:06.940816	1
6613	223	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:07.339325	2025-06-14 19:38:07.33933	1
6614	224	2025-06-13	\N	\N	present	\N	2025-06-14 19:38:07.428639	2025-06-14 19:38:07.428644	1
6615	223	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:07.51718	2025-06-14 19:38:07.517185	1
6616	224	2025-06-14	\N	\N	present	\N	2025-06-14 19:38:07.609287	2025-06-14 19:38:07.609289	1
6617	184	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:29.768755	2025-06-15 08:23:29.76876	1
6618	185	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:29.869106	2025-06-15 08:23:29.86911	1
6619	186	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:29.957085	2025-06-15 08:23:29.95709	1
6620	187	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:30.043971	2025-06-15 08:23:30.043975	1
6621	188	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:30.130562	2025-06-15 08:23:30.130565	1
6622	175	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:30.526139	2025-06-15 08:23:30.526143	1
6623	178	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:30.612436	2025-06-15 08:23:30.61244	1
6624	180	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:30.699073	2025-06-15 08:23:30.699077	1
6625	182	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:30.785178	2025-06-15 08:23:30.785183	1
6626	173	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:30.871386	2025-06-15 08:23:30.87139	1
6627	172	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:30.959419	2025-06-15 08:23:30.959423	1
6628	171	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:31.045708	2025-06-15 08:23:31.045713	1
6629	174	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:31.132485	2025-06-15 08:23:31.132489	1
6630	177	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:31.219502	2025-06-15 08:23:31.219506	1
6631	169	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:31.307403	2025-06-15 08:23:31.307407	1
6632	183	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:31.400935	2025-06-15 08:23:31.400939	1
6633	181	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:31.487271	2025-06-15 08:23:31.487275	1
6634	179	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:31.573902	2025-06-15 08:23:31.573906	1
6635	226	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:31.661657	2025-06-15 08:23:31.661662	1
6636	227	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:31.747797	2025-06-15 08:23:31.747798	1
6637	193	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:32.157487	2025-06-15 08:23:32.157492	1
6638	191	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:32.261566	2025-06-15 08:23:32.261571	1
6639	189	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:32.347924	2025-06-15 08:23:32.347928	1
6640	190	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:32.433999	2025-06-15 08:23:32.434004	1
6641	192	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:32.520286	2025-06-15 08:23:32.520288	1
6642	194	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:32.91468	2025-06-15 08:23:32.914684	1
6643	195	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.001048	2025-06-15 08:23:33.001052	1
6644	196	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.087719	2025-06-15 08:23:33.087723	1
6645	197	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.187924	2025-06-15 08:23:33.187929	1
6646	200	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.281628	2025-06-15 08:23:33.281633	1
6647	202	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.367592	2025-06-15 08:23:33.367596	1
6648	203	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.453527	2025-06-15 08:23:33.453531	1
6649	205	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.549022	2025-06-15 08:23:33.549026	1
6650	206	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.635019	2025-06-15 08:23:33.635023	1
6651	207	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.734672	2025-06-15 08:23:33.734677	1
6652	208	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.820778	2025-06-15 08:23:33.820782	1
6653	209	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.906662	2025-06-15 08:23:33.906666	1
6654	198	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:33.992569	2025-06-15 08:23:33.992573	1
6655	201	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:34.078544	2025-06-15 08:23:34.078548	1
6657	214	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:34.251344	2025-06-15 08:23:34.251348	1
6658	225	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:34.340646	2025-06-15 08:23:34.34065	1
6659	230	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:34.429255	2025-06-15 08:23:34.42926	1
6660	231	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:34.519079	2025-06-15 08:23:34.51908	1
6661	216	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:34.906726	2025-06-15 08:23:34.90673	1
6662	217	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:34.993278	2025-06-15 08:23:34.993282	1
6663	218	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:35.079427	2025-06-15 08:23:35.079431	1
6664	219	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:35.16594	2025-06-15 08:23:35.165944	1
6665	220	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:35.253096	2025-06-15 08:23:35.2531	1
6666	221	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:35.338984	2025-06-15 08:23:35.338988	1
6667	222	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:35.425067	2025-06-15 08:23:35.425069	1
6668	223	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:35.810824	2025-06-15 08:23:35.810828	1
6669	224	2025-06-15	\N	\N	present	\N	2025-06-15 08:23:35.896648	2025-06-15 08:23:35.89665	1
6670	184	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:19.182172	2025-06-16 15:46:19.182177	1
6671	185	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:19.28224	2025-06-16 15:46:19.282245	1
6672	186	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:19.374166	2025-06-16 15:46:19.374171	1
6673	187	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:19.465548	2025-06-16 15:46:19.465553	1
6674	188	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:19.556558	2025-06-16 15:46:19.556559	1
6675	175	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:19.975883	2025-06-16 15:46:19.975888	1
6676	178	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:20.074797	2025-06-16 15:46:20.074802	1
6677	180	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:20.166765	2025-06-16 15:46:20.16677	1
6678	182	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:20.258028	2025-06-16 15:46:20.258034	1
6679	173	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:20.348941	2025-06-16 15:46:20.348947	1
6680	172	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:20.442358	2025-06-16 15:46:20.442363	1
6681	171	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:20.533286	2025-06-16 15:46:20.533291	1
6682	174	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:20.626864	2025-06-16 15:46:20.626869	1
6683	177	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:20.720945	2025-06-16 15:46:20.72095	1
6684	169	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:20.812816	2025-06-16 15:46:20.812821	1
6686	181	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:21.004452	2025-06-16 15:46:21.004456	1
6687	179	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:21.095239	2025-06-16 15:46:21.095244	1
6688	226	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:21.18603	2025-06-16 15:46:21.186034	1
6689	227	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:21.277442	2025-06-16 15:46:21.27745	1
6690	193	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:21.700724	2025-06-16 15:46:21.700729	1
6691	191	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:21.791255	2025-06-16 15:46:21.79126	1
6692	189	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:21.882508	2025-06-16 15:46:21.882514	1
6693	190	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:21.986924	2025-06-16 15:46:21.986928	1
6694	192	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:22.078708	2025-06-16 15:46:22.07871	1
6695	194	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:22.484887	2025-06-16 15:46:22.484892	1
6696	195	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:22.583487	2025-06-16 15:46:22.583491	1
6697	196	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:22.674322	2025-06-16 15:46:22.674327	1
6698	197	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:22.766766	2025-06-16 15:46:22.766771	1
6699	200	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:22.857304	2025-06-16 15:46:22.857309	1
6700	202	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:22.947635	2025-06-16 15:46:22.94764	1
6701	203	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:23.03867	2025-06-16 15:46:23.038675	1
6702	205	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:23.129835	2025-06-16 15:46:23.12984	1
6703	206	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:23.220836	2025-06-16 15:46:23.220841	1
6704	207	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:23.312217	2025-06-16 15:46:23.312222	1
6705	208	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:23.403993	2025-06-16 15:46:23.403998	1
6706	209	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:23.548726	2025-06-16 15:46:23.548732	1
6707	198	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:23.639657	2025-06-16 15:46:23.639663	1
6708	201	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:23.7331	2025-06-16 15:46:23.733105	1
6709	204	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:23.824116	2025-06-16 15:46:23.824121	1
6710	214	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:23.915045	2025-06-16 15:46:23.91505	1
6711	225	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:24.005405	2025-06-16 15:46:24.00541	1
6712	230	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:24.097179	2025-06-16 15:46:24.097183	1
6713	231	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:24.188254	2025-06-16 15:46:24.188256	1
6714	216	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:24.595502	2025-06-16 15:46:24.595507	1
6715	217	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:24.687823	2025-06-16 15:46:24.687828	1
6716	218	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:24.778722	2025-06-16 15:46:24.778727	1
6717	219	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:24.870413	2025-06-16 15:46:24.870418	1
6718	220	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:24.961012	2025-06-16 15:46:24.961018	1
6719	221	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:25.052397	2025-06-16 15:46:25.052402	1
6720	222	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:25.144407	2025-06-16 15:46:25.144408	1
6721	223	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:25.563691	2025-06-16 15:46:25.563695	1
6722	224	2025-06-16	\N	\N	present	\N	2025-06-16 15:46:25.657243	2025-06-16 15:46:25.657245	1
6723	184	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:09.299811	2025-06-17 19:15:09.299816	1
6724	185	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:09.398959	2025-06-17 19:15:09.398963	1
6725	186	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:09.487991	2025-06-17 19:15:09.487997	1
6726	187	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:09.577135	2025-06-17 19:15:09.57714	1
6727	188	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:09.663847	2025-06-17 19:15:09.663849	1
6728	175	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.066803	2025-06-17 19:15:10.066808	1
6729	178	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.168523	2025-06-17 19:15:10.168527	1
6730	180	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.263953	2025-06-17 19:15:10.263958	1
6731	182	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.352864	2025-06-17 19:15:10.352868	1
6732	173	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.439732	2025-06-17 19:15:10.439737	1
6733	172	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.526522	2025-06-17 19:15:10.526527	1
6734	171	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.614196	2025-06-17 19:15:10.6142	1
6735	174	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.703065	2025-06-17 19:15:10.70307	1
6736	177	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.791921	2025-06-17 19:15:10.791926	1
6737	169	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.879467	2025-06-17 19:15:10.879472	1
6738	183	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:10.969835	2025-06-17 19:15:10.969839	1
6739	181	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:11.062202	2025-06-17 19:15:11.062207	1
6740	179	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:11.149041	2025-06-17 19:15:11.149046	1
6741	226	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:11.246823	2025-06-17 19:15:11.246828	1
6742	227	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:11.334481	2025-06-17 19:15:11.334483	1
6743	193	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:11.727789	2025-06-17 19:15:11.727794	1
6744	191	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:11.814573	2025-06-17 19:15:11.814578	1
6745	189	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:11.905616	2025-06-17 19:15:11.905643	1
6746	190	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:11.992187	2025-06-17 19:15:11.992191	1
6747	192	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:12.079977	2025-06-17 19:15:12.079978	1
6748	194	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:12.471133	2025-06-17 19:15:12.471138	1
6749	195	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:12.558401	2025-06-17 19:15:12.558434	1
6750	196	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:12.649049	2025-06-17 19:15:12.649055	1
6751	197	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:12.737273	2025-06-17 19:15:12.737284	1
6752	200	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:12.830039	2025-06-17 19:15:12.830044	1
6753	202	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:12.9219	2025-06-17 19:15:12.921905	1
6754	203	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.008668	2025-06-17 19:15:13.008673	1
6755	205	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.096153	2025-06-17 19:15:13.096158	1
6756	206	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.182951	2025-06-17 19:15:13.182956	1
6757	207	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.276051	2025-06-17 19:15:13.276055	1
6758	208	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.362956	2025-06-17 19:15:13.362961	1
6759	209	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.449956	2025-06-17 19:15:13.44996	1
6760	198	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.536629	2025-06-17 19:15:13.536634	1
6761	201	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.623281	2025-06-17 19:15:13.623286	1
6762	204	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.711793	2025-06-17 19:15:13.711798	1
6763	214	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.798808	2025-06-17 19:15:13.798812	1
6764	225	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.887054	2025-06-17 19:15:13.887087	1
6765	230	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:13.97399	2025-06-17 19:15:13.973994	1
6766	231	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:14.060518	2025-06-17 19:15:14.060519	1
6767	216	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:14.456355	2025-06-17 19:15:14.456359	1
6768	217	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:14.543249	2025-06-17 19:15:14.543254	1
6769	218	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:14.630002	2025-06-17 19:15:14.630006	1
6770	219	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:14.724681	2025-06-17 19:15:14.724686	1
6771	220	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:14.811501	2025-06-17 19:15:14.811506	1
6772	221	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:14.905984	2025-06-17 19:15:14.905989	1
6773	222	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:14.993152	2025-06-17 19:15:14.993154	1
6774	223	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:15.383286	2025-06-17 19:15:15.383292	1
6775	224	2025-06-17	\N	\N	present	\N	2025-06-17 19:15:15.47253	2025-06-17 19:15:15.472532	1
6776	184	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:44.839964	2025-06-18 09:22:44.839969	1
6777	185	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:44.938344	2025-06-18 09:22:44.938349	1
6778	186	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:45.026385	2025-06-18 09:22:45.026391	1
6779	187	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:45.114342	2025-06-18 09:22:45.114348	1
6780	188	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:45.202661	2025-06-18 09:22:45.202663	1
6781	175	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:45.605624	2025-06-18 09:22:45.605632	1
6782	178	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:45.692954	2025-06-18 09:22:45.692959	1
6783	180	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:45.780676	2025-06-18 09:22:45.780681	1
6784	182	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:45.868867	2025-06-18 09:22:45.868873	1
6785	173	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:45.958047	2025-06-18 09:22:45.958054	1
6786	172	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:46.047798	2025-06-18 09:22:46.047804	1
6787	171	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:46.138583	2025-06-18 09:22:46.138592	1
6788	174	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:46.226276	2025-06-18 09:22:46.226282	1
6789	177	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:46.313714	2025-06-18 09:22:46.313719	1
6790	169	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:46.403612	2025-06-18 09:22:46.403618	1
6791	183	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:46.4918	2025-06-18 09:22:46.491808	1
6792	181	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:46.721497	2025-06-18 09:22:46.721504	1
6793	179	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:46.809274	2025-06-18 09:22:46.809279	1
6794	226	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:46.896919	2025-06-18 09:22:46.896924	1
6795	227	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:46.985207	2025-06-18 09:22:46.985209	1
6796	193	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:47.385896	2025-06-18 09:22:47.385902	1
6797	191	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:47.472929	2025-06-18 09:22:47.472934	1
6798	189	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:47.560394	2025-06-18 09:22:47.5604	1
6799	190	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:47.647589	2025-06-18 09:22:47.647594	1
6800	192	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:47.737527	2025-06-18 09:22:47.737529	1
6801	194	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:48.137443	2025-06-18 09:22:48.137449	1
6802	195	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:48.225513	2025-06-18 09:22:48.225519	1
6803	196	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:48.314549	2025-06-18 09:22:48.314559	1
6804	197	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:48.402481	2025-06-18 09:22:48.402486	1
6805	200	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:48.489886	2025-06-18 09:22:48.489893	1
6806	202	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:48.581955	2025-06-18 09:22:48.581965	1
6807	203	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:48.669921	2025-06-18 09:22:48.669927	1
6808	205	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:48.763733	2025-06-18 09:22:48.763739	1
6809	206	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:48.851473	2025-06-18 09:22:48.851479	1
6810	207	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:48.938916	2025-06-18 09:22:48.938921	1
6811	208	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:49.02767	2025-06-18 09:22:49.027675	1
6812	209	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:49.115161	2025-06-18 09:22:49.115166	1
6813	198	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:49.202432	2025-06-18 09:22:49.202438	1
6814	201	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:49.289966	2025-06-18 09:22:49.289971	1
6815	204	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:49.377272	2025-06-18 09:22:49.377277	1
6816	214	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:49.465234	2025-06-18 09:22:49.46524	1
6817	225	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:49.552577	2025-06-18 09:22:49.552583	1
6818	230	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:49.640224	2025-06-18 09:22:49.640229	1
6819	231	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:49.727407	2025-06-18 09:22:49.727408	1
6820	216	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:50.117959	2025-06-18 09:22:50.117964	1
6821	217	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:50.207058	2025-06-18 09:22:50.207064	1
6822	218	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:50.367759	2025-06-18 09:22:50.367764	1
6823	219	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:50.45567	2025-06-18 09:22:50.455676	1
6824	220	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:50.543505	2025-06-18 09:22:50.543511	1
6825	221	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:50.630962	2025-06-18 09:22:50.630969	1
6826	222	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:50.723595	2025-06-18 09:22:50.723596	1
6827	223	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:51.117275	2025-06-18 09:22:51.11728	1
6828	224	2025-06-18	\N	\N	present	\N	2025-06-18 09:22:51.204826	2025-06-18 09:22:51.204828	1
6685	183	2025-06-16	\N	\N	present	عذر طبي وتم ارسال الايجازة المرضية 	2025-06-16 15:46:20.911025	2025-06-20 23:40:53.865854	1
\.


--
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.audit_log (id, user_id, action, entity_type, entity_id, details, ip_address, user_agent, previous_data, new_data, "timestamp") FROM stdin;
56	8	تحديث الصلاحيات	مستخدم	9	تم تحديث صلاحيات المستخدم زياد محمد علي حسن	\N	\N	\N	\N	2025-06-20 22:47:30.525658
57	8	تحديث الصلاحيات	مستخدم	9	تم تحديث صلاحيات المستخدم زياد محمد علي حسن	\N	\N	\N	\N	2025-06-20 22:47:32.243212
58	8	create	vehicle_handover	7	تم إنشاء نموذج تسليم للسيارة: 3228 ب س ن	109.82.101.116, 10.81.3.14	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 10:32:39.234377
59	8	create	vehicle_handover	8	تم إنشاء نموذج تسليم للسيارة: 3206- ب س ن	109.82.101.116, 10.81.11.198	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 10:48:00.267686
60	8	create	vehicle_handover	9	تم إنشاء نموذج تسليم (موبايل) للسيارة: 1493- ب س ق	109.82.101.116, 10.81.10.202	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 11:04:27.073285
61	8	update	Employee	232	تم تحديث بيانات الموظف: MD YOUSUB ALI	176.123.17.182, 10.81.11.198	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0	\N	\N	2025-07-06 11:57:45.743509
62	8	update	Employee	186	تم تحديث بيانات الموظف: SOZAN MIA	176.123.17.182, 10.81.11.198	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0	\N	\N	2025-07-06 11:59:46.76991
63	8	update	Employee	232	تم تحديث بيانات الموظف: MD YOUSUB ALI	176.123.17.182, 10.81.7.55	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0	\N	\N	2025-07-06 12:06:02.43013
64	8	update	Employee	232	تم تحديث بيانات الموظف: MD YOUSUB ALI	176.123.17.182, 10.81.11.198	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0	\N	\N	2025-07-06 12:06:22.026307
65	8	export	vehicle_workshop	12	تم تصدير سجلات ورشة السيارة 1493- ب س ق إلى PDF	109.82.101.116, 10.81.7.55	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 12:15:22.689288
66	8	create	vehicle_workshop	31	تم إضافة سجل دخول الورشة للسيارة: ABC-123	176.123.17.182, 10.81.2.204	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0	\N	\N	2025-07-06 12:17:41.74298
67	8	update	vehicle_workshop	31	تم تعديل سجل الورشة للسيارة ABC-123	176.123.17.182, 10.81.4.152	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0	\N	\N	2025-07-06 12:18:10.421673
68	8	create	vehicle_workshop	32	تم إضافة سجل دخول الورشة للسيارة: 3204 - ب س ن من الجوال	176.123.17.182, 10.81.7.55	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0	\N	\N	2025-07-06 12:26:04.778125
69	8	create	vehicle_handover	10	تم إنشاء نموذج استلام للسيارة: 3218- ب س ن	109.82.101.116, 10.81.3.14	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 14:00:16.618606
70	8	update	vehicle_handover	10	تم تعديل نموذج استلام للسيارة: 3218- ب س ن	109.82.101.116, 10.81.7.55	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 14:34:15.731072
71	8	update	vehicle_handover	12	تم تعديل نموذج تسليم للسيارة: 3218- ب س ن	109.82.101.116, 10.81.10.202	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 14:49:20.302419
72	8	create	vehicle_handover	13	تم إنشاء نموذج استلام للسيارة: 3218- ب س ن	109.82.101.116, 10.81.2.204	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 15:03:25.653991
73	8	create	vehicle_handover	14	تم إنشاء نموذج استلام (موبايل) للسيارة: 3218- ب س ن	109.82.101.116, 10.81.4.152	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36	\N	\N	2025-07-06 15:09:07.366595
74	8	create	vehicle_handover	17	تم إنشاء نموذج استلام (موبايل) للسيارة: ABC-123	109.82.101.116, 10.81.4.152	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 16:05:21.570403
75	8	create	vehicle_handover	18	تم إنشاء نموذج استلام (موبايل) للسيارة: ABC-123	109.82.101.116, 10.81.10.202	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 16:12:40.679496
76	8	create	vehicle_handover	19	تم إنشاء نموذج استلام (موبايل) للسيارة: ABC-123	109.82.101.116, 10.81.4.152	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 16:18:13.51346
77	8	delete	vehicle_handover	19	تم حذف سجل استلام للسيارة ABC-123	109.82.101.116, 10.81.2.204	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-06 16:24:02.318894
78	9	create	vehicle_handover	20	تم إنشاء نموذج استلام (موبايل) للسيارة: ABC-123	109.82.101.116, 10.81.3.14	Mozilla/5.0 (iPad; CPU OS 18_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Mobile/15E148 Safari/604.1	\N	\N	2025-07-06 16:29:37.702721
79	8	update	Employee	178	تم تحديث بيانات الموظف: SHABEER MULLA PALLI	109.82.101.116, 10.81.9.45	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-07 20:15:34.252468
80	8	update	Employee	178	تم تحديث بيانات الموظف: SHABEER MULLA PALLI	109.82.101.116, 10.81.12.31	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-07 20:15:35.29305
81	8	update	Employee	180	تم تحديث بيانات الموظف: HUSSAM AL DAIN	109.82.101.116, 10.81.10.168	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-07 20:15:53.553764
82	8	update	Employee	173	تم تحديث بيانات الموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI	109.82.101.116, 10.81.5.230	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-07 20:16:15.473521
83	8	update	Employee	172	تم تحديث بيانات الموظف: ‏HASAN MOHAMMED ALI RAGEH‏	109.82.101.116, 10.81.10.168	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-07 20:16:42.180442
84	8	update	Employee	171	تم تحديث بيانات الموظف: WADHAH NABIL QASEM QAID AL TAHERI	109.82.101.116, 10.81.9.45	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-07 20:17:23.640703
85	8	update	Employee	220	تم تحديث بيانات الموظف: MEHEDI KHAN	109.82.101.116, 10.81.5.230	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-07 20:24:26.838394
86	8	create	vehicle_workshop	33	تم إضافة سجل دخول الورشة للسيارة: ABC-123 من الجوال	109.82.101.116, 10.81.12.31	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-07 22:36:00.5572
87	8	create	vehicle_workshop	44	تم إضافة سجل دخول الورشة للسيارة: ABC-123 من الجوال	109.82.101.116, 10.81.12.31	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-07 22:53:40.647238
88	8	create	vehicle_handover	25	تم إنشاء نموذج تسليم (موبايل) للسيارة: ABC-123	109.82.101.116, 10.81.5.230	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0	\N	\N	2025-07-07 22:58:44.359521
89	8	delete	vehicle_workshop	\N	تم حذف سجل دخول الورشة للسيارة: ABC-123 - الوصف: وصف من الجوال	109.82.101.116, 10.81.8.186	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36	\N	\N	2025-07-07 23:20:33.635002
90	8	update	vehicle_workshop	\N	تم تعديل سجل دخول الورشة للسيارة: ABC-123 من الجوال	109.82.101.116, 10.81.5.239	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36	\N	\N	2025-07-08 16:22:08.570435
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.companies (id, name, contact_email, contact_phone, address, status, is_trial, trial_start_date, trial_end_date, trial_days, trial_extended, subscription_start_date, subscription_end_date, subscription_status, subscription_plan, max_users, max_employees, max_vehicles, max_departments, monthly_fee, last_payment_date, next_payment_due, created_at, updated_at) FROM stdin;
1	الشركة الرئيسية	admin@nuzum.sa	+966501234567	الرياض، المملكة العربية السعودية	active	\N	\N	\N	\N	\N	\N	\N	\N	enterprise	\N	1000	1000	\N	\N	\N	\N	2025-06-20 22:37:05.270392	2025-06-20 22:37:05.270392
3	شركة التيار السريع	skrkhtan@gmail.com	+966543949265		active	f	\N	\N	30	f	\N	\N	active	basic	5	25	10	5	0	\N	\N	2025-06-20 23:46:01.031671	2025-06-20 23:46:01.031674
2	شركة تجريبية	test@company.com	966501234567	الرياض	inactive	f	\N	\N	30	f	\N	\N	active	basic	5	25	10	5	0	\N	\N	2025-06-20 23:44:08.696905	2025-06-21 00:25:37.784011
\.


--
-- Data for Name: company_permissions; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.company_permissions (id, company_id, module_name, permissions, is_enabled, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: company_subscriptions; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.company_subscriptions (id, company_id, plan_type, is_trial, trial_start_date, trial_end_date, start_date, end_date, is_active, auto_renew, created_at, updated_at) FROM stdin;
1	1	enterprise	f	\N	\N	2025-06-20 22:37:33.215102	2026-06-20 22:37:33.215102	t	t	2025-06-20 22:37:33.215102	2025-06-20 22:37:33.215102
2	2	trial	t	\N	\N	2025-06-20 00:00:00	2025-07-20 00:00:00	t	f	2025-06-20 23:44:08.747642	2025-06-20 23:44:08.747644
3	3	trial	t	\N	\N	2025-06-20 00:00:00	2025-07-20 00:00:00	t	f	2025-06-20 23:46:01.081881	2025-06-20 23:46:01.081883
\.


--
-- Data for Name: department; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.department (id, name, description, manager_id, created_at, updated_at, company_id) FROM stdin;
2	Aramex Liber	قسم القواء العاملة	\N	2025-04-16 15:52:00.760934	2025-04-16 15:52:00.760936	1
1	Aramex Coruer	مندوبين توصيل طرود بريديه	\N	2025-04-15 21:12:45.021039	2025-04-16 15:55:15.159672	1
3	DHL	مندوبين   توصل طرود	\N	2025-04-17 23:45:36.809506	2025-04-17 23:45:36.809511	1
4	FLOW	سائقين وعمال تشغيل 	\N	2025-04-22 10:37:42.572936	2025-04-22 10:37:42.572941	1
5	Suleiman Al Habib	عمال تشغيل 	\N	2025-04-22 11:03:45.02687	2025-04-22 11:03:45.026875	1
6	Project Supervisors	مشرفين المشريع	\N	2025-04-22 20:00:49.217299	2025-04-22 20:00:49.217304	1
7	قسم تقني	\N	\N	2025-07-06 10:06:49.535441	\N	1
\.


--
-- Data for Name: document; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.document (id, employee_id, document_type, document_number, issue_date, expiry_date, notes, created_at, updated_at) FROM stdin;
12	223	national_id	2458097736	2025-02-04	2025-08-02		2025-04-22 19:55:00.551068	2025-05-12 06:27:44.295014
59	201	national_id	ID-2515488746      	\N	2025-07-31		2025-04-25 18:41:02.988751	2025-05-18 10:48:03.801647
18	191	national_id	2334132780	2025-01-30	2025-07-29		2025-04-23 13:10:05.225337	2025-05-18 10:55:29.510389
13	180	national_id	2469288936	2025-04-14	2025-07-14		2025-04-22 20:25:55.403852	2025-04-22 20:25:55.403857
20	194	national_id	2519934745	2025-04-03	2025-07-03		2025-04-23 13:25:35.951213	2025-04-23 13:25:35.951218
25	206	national_id	2526010738	2025-04-18	2025-07-18		2025-04-23 18:14:01.782005	2025-04-23 18:14:01.78201
26	203	national_id	2557678071	2025-01-09	2025-04-09		2025-04-25 14:47:30.860177	2025-04-25 14:47:30.860181
34	210	national_id	2586705465	2025-04-25	2025-10-27		2025-04-25 16:56:14.365196	2025-04-25 16:56:14.365202
65	220	national_id	2536463736	2025-01-03	2025-03-04		2025-04-26 16:51:13.448758	2025-04-26 16:51:13.448763
66	221	national_id	2536463587	2025-01-03	2025-03-04		2025-04-26 16:52:56.68436	2025-04-26 16:52:56.684366
60	204	national_id	ID-2486812155     	\N	2025-07-10		2025-04-25 18:41:03.132812	2025-04-26 17:07:09.679073
14	189	national_id	2512445616	2025-02-08	2025-08-06		2025-04-23 12:43:25.678033	2025-05-18 11:04:00.625871
32	214	national_id	2506174503	2025-02-04	2025-08-02		2025-04-25 15:19:30.357259	2025-05-18 11:04:44.988379
19	192	national_id	2300844764	2025-02-15	2025-08-15		2025-04-23 13:11:31.568752	2025-05-21 15:01:52.551977
24	208	national_id	2567648189	2025-02-11	2025-08-09		2025-04-23 18:12:19.087071	2025-05-26 10:17:00.244334
33	197	national_id	2498036686	2025-02-17	2025-08-15		2025-04-25 16:54:28.671568	2025-05-26 10:27:32.972343
22	205	national_id	2372117297	2025-01-12	2025-08-10		2025-04-23 18:07:57.683019	2025-05-26 10:30:25.993296
76	225	national_id	2529580017	2025-02-02	2025-08-21		2025-05-26 10:54:22.741019	2025-05-28 10:14:31.380688
30	195	national_id	2546281417	2025-03-03	2025-09-01		2025-04-25 15:06:47.587838	2025-06-15 07:39:33.654489
17	224	national_id	2290833975	2025-03-09	2025-09-07		2025-04-23 12:54:47.411781	2025-06-15 07:40:38.800881
16	193	national_id	2516571086	2025-03-11	2025-09-11		2025-04-23 12:46:03.650912	2025-06-24 11:51:49.023943
15	190	national_id	2383840655	2025-03-11	2025-09-09		2025-04-23 12:44:53.552875	2025-06-24 12:03:07.83133
21	196	national_id	2522454046	2025-03-25	2025-09-23		2025-04-23 13:28:29.396845	2025-06-28 10:58:43.219685
27	200	national_id	2556738348	2025-03-06	2025-09-07		2025-04-25 14:48:53.734933	2025-06-28 11:07:49.48972
11	175	national_id	250206529	2025-03-01	2025-08-28		2025-04-22 19:50:30.605727	2025-07-01 13:50:05.708742
23	207	national_id	2563959242	2025-03-28	2025-09-26		2025-04-23 18:09:20.488495	2025-07-01 14:12:26.581759
31	209	national_id	2571312541	2025-02-01	2025-09-28		2025-04-25 15:13:35.554298	2025-07-02 15:01:38.103965
29	202	national_id	2555371539	2025-01-17	2025-09-13		2025-04-25 14:53:22.279156	2025-07-02 15:02:10.764521
\.


--
-- Data for Name: employee; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.employee (id, employee_id, national_id, name, mobile, email, job_title, status, location, project, department_id, join_date, created_at, updated_at, nationality, contract_type, basic_salary, has_national_balance, profile_image, national_id_image, license_image, company_id, "mobilePersonal", nationality_id, contract_status, license_status) FROM stdin;
175	8621.0	2502086529	MOHAMMED MOQBEL M. ABDULLAH GHANEM	543949234	None@n.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:15.129961	2025-07-06 13:40:50.892995	\N	foreign	0	f	\N	\N	\N	1	0506806948	13	Active	Valid
178	4299.0	2510686195.0	SHABEER MULLA PALLI	591014696	None@n.com	courier	active	Qassim	None	1	\N	2025-04-21 16:56:16.284087	2025-07-07 20:15:33.725038	\N	foreign	0	f	\N	\N	\N	1		\N		
180	1910	2469288936.0	HUSSAM AL DAIN	533378054	1910@f.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:17.061889	2025-07-07 20:15:53.059573	\N	foreign	0	f	uploads/employees/1910_profile_20250529_122256.jpg	\N	\N	1		\N		
182	4644.0	2522852637.0	MUHAMMAD USMAN MUHAMMAD MAQBOOL	593214404	None@n.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:17.832618	2025-07-08 18:34:10.40963	\N	foreign	0	f	\N	\N	\N	1		\N		
210	80120	2586705465	AFAZ UDDIN	05xxxxxxxx	None@n.com	موظف	inactive	Hail - HUB	None	4	\N	2025-04-22 10:38:08.730594	2025-06-02 14:47:58.588424	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
186	3690	4727638118	SOZAN MIA	05xxxxxxxx	95432@gmail.com	Labor	active	QASSIM	Aramex Labor	2	\N	2025-04-21 17:41:36.715776	2025-07-06 11:59:46.297468	\N	foreign	0	f	\N	\N	\N	1	876543	\N		Suspended
173	50342	2532825060	MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI	0592746970	None@n.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:14.360945	2025-07-07 20:16:14.971303	\N	foreign	0	f	\N	\N	\N	1		\N		
172	50603.0	2476531674.0	‏HASAN MOHAMMED ALI RAGEH‏	0501444365	None@n.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:13.969511	2025-07-07 20:16:41.683451	\N	foreign	0	f	\N	\N	\N	1		\N		
171	50458.0	2505050688.0	WADHAH NABIL QASEM QAID AL TAHERI	561706279	None@n.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:13.58352	2025-07-07 20:17:23.137688	\N	foreign	0	f	\N	\N	\N	1		13		
220	50837	2536463736	MEHEDI KHAN	576457174.0	None@n.com	LABOR	active	QASSIM	None	5	\N	2025-04-22 11:06:27.503929	2025-07-07 20:24:26.262071	\N	foreign	0	f	\N	\N	\N	1		\N		
223	3288	3288	ZEYAD MOHAMMAD ALI HASAN	0593214413	z.alhamdani@rassaudi.com	SOPRVAZAR	active	Qassim	DHL	6	\N	2025-04-22 19:53:28.351789	2025-07-08 21:00:04.789568	\N	foreign	0	f	\N	\N	\N	1		\N		
214	8885	2506174503	ARSLAN ZAFAR AHMED	05xxxxxxxx	\N	موظف	active	Hail - HUB	\N	4	\N	2025-04-22 10:38:09.818831	2025-04-22 10:38:09.818836	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
212	    50308	         2601216571	MEHEDI HASAN	0535684265	None@n.com	LABOR	inactive	Hail - HUB	FLOW	4	\N	2025-04-22 10:38:09.258481	2025-05-17 10:14:33.915623	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
174	50685.0	2370503332.0	ABBAS AMEEN QAID QASEM	545593215	None@n.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:14.74653	2025-04-21 17:04:47.445995	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
177	50798.0	2584266882.0	TAHIR ALI MEHBOOB ALI	569280107	None@n.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:15.899229	2025-04-21 17:05:14.792879	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
169	50799.0	2499161459.0	‏SALEH NASSER YASLAM BAANS	501444835	None@n.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:12.81374	2025-04-21 17:05:43.370958	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
176	50835.0	2539476297.0	MOHAMED MUBARK YOUSIF ELAMIN	545592624	None@n.com	courier	active	Qassim	Aramex	\N	\N	2025-04-21 16:56:15.513954	2025-04-21 17:06:05.896455	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
184	3555	2496176153	MD RABBI	05xxxxxxxx	\N	Labor	active	QASSIM	Aramex Labor	2	\N	2025-04-21 17:41:36.171842	2025-04-21 17:41:36.171845	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
185	3553	A01234767	NASIR UDDIN	05xxxxxxxx	\N	Labor	active	QASSIM	Aramex Labor	2	\N	2025-04-21 17:41:36.452282	2025-04-21 17:41:36.452286	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
187	3556	4746723685	SHABUDDIN HABIB	05xxxxxxxx	\N	Labor	active	QASSIM	Aramex Labor	2	\N	2025-04-21 17:41:36.985581	2025-04-21 17:41:36.985585	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
188	3849	4746688904	MD RATAN MIAH MD HOBI	05xxxxxxxx	\N	Labor	active	QASSIM	Aramex Labor	2	\N	2025-04-21 17:41:37.248702	2025-04-21 17:41:37.248705	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
183	4350.0	2496090594.0	‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI	0569280132	None@n.com	courier	active	Hail	Aramex	1	\N	2025-04-21 16:56:18.226433	2025-05-18 16:25:40.637489	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
193	8804	2516571086	ALI ELSAYED ALI ABDALLA	0550407908	None@n.com	courier	active	Qassim	DHL	3	\N	2025-04-22 10:27:59.160183	2025-04-22 10:27:59.160188	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
194	8410	2519934745	SAGAR DAS NIMEI CHARAN	570504402	\N	570504402	active	Qasim	\N	4	\N	2025-04-22 10:38:04.475982	2025-04-22 10:38:04.475987	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
216	50211	2576898544	ABDULL KYUAM	562283012.0	\N	LABOR	active	QASSIM	\N	5	\N	2025-04-22 11:06:26.385293	2025-04-22 11:06:26.385298	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
217	50209	2477211961	KAZI TOUFIQUL ISLAM	532695974.0	\N	LABOR	active	QASSIM	\N	5	\N	2025-04-22 11:06:26.668355	2025-04-22 11:06:26.66836	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
218	50627	A12194120	MD ESHAQ BANGLADESHI	05xxxxxxxx	\N	LABOR	active	QASSIM	\N	5	\N	2025-04-22 11:06:26.94469	2025-04-22 11:06:26.944695	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
219	50207	2575461278	MD MUNZURUL ISLAM	532726647.0	\N	LABOR	active	QASSIM	\N	5	\N	2025-04-22 11:06:27.242071	2025-04-22 11:06:27.242076	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
221	50838	2536463587	MD SAIFUR RAHMAN MAHEDI	578614254.0	\N	LABOR	active	QASSIM	\N	5	\N	2025-04-22 11:06:27.766494	2025-04-22 11:06:27.766499	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
222	50262	2577180983	RASEL MD	573013326.0	\N	LABOR	active	QASSIM	\N	5	\N	2025-04-22 11:06:28.030592	2025-04-22 11:06:28.030597	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
190	8784	2383840655	FRID MOKHTAR AHMED ANABA	0567567726	None@n.com	Tanker	active	Qassim	DHL	3	2023-12-14	2025-04-22 10:20:09.117037	2025-04-23 10:38:58.971258	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
192	8785	2300844764	Musab Qasim Allah Muhammad Ahmed Khair Al-Sayyid	0581913411	None@n.com	courier	active	Qassim	DHL	3	\N	2025-04-22 10:26:08.150371	2025-04-23 10:39:49.196648	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
195	8938	2546281417	MOHAMMED ASIF MOHAMMED TUFAIL 	541231751	\N	541231751	active	Qasim	\N	4	\N	2025-04-22 10:38:04.74753	2025-04-22 10:38:04.747535	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
196	8402	2522454046	SEKH AKRAM SEKH SULAIMAN	‎054 130 7025	\N	‎054 130 7025	active	Qasim	\N	4	\N	2025-04-22 10:38:05.018617	2025-04-22 10:38:05.018622	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
197	5574	2498036686	MD JOSIM UDDIN MD	541812049	\N	541812049	active	Qasim	\N	4	\N	2025-04-22 10:38:05.283533	2025-04-22 10:38:05.283538	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
200	8796	2556738348	IDREES KHURSHID	05xxxxxxxx	\N	موظف	active	Qasim	\N	4	\N	2025-04-22 10:38:06.077808	2025-04-22 10:38:06.077813	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
202	8774	2555371539	MUHAMMAD MUNEEB SULTANI GUL	05xxxxxxxx	\N	موظف	active	Qasim	\N	4	\N	2025-04-22 10:38:06.611748	2025-04-22 10:38:06.611753	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
203	8882	2557678071	SAJJAD HUSSAIN KHAYAL GUL	05xxxxxxxx	\N	موظف	active	Qasim	\N	4	\N	2025-04-22 10:38:06.878276	2025-04-22 10:38:06.878281	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
205	8081	2372117297	Billal Abu	05xxxxxxxx	\N	موظف	active	ArAr	\N	4	\N	2025-04-22 10:38:07.404227	2025-04-22 10:38:07.404232	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
206	8970	2526010737	Md forkan	05xxxxxxxx	\N	موظف	active	ArAr	\N	4	\N	2025-04-22 10:38:07.667725	2025-04-22 10:38:07.66773	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
207	80051	2563959242	MD SIAM	05xxxxxxxx	\N	موظف	active	ArAr	\N	4	\N	2025-04-22 10:38:07.932467	2025-04-22 10:38:07.932471	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
208	4924	2567648189	MD SANOARUL ISLAM	05xxxxxxxx	\N	موظف	active	ArAr	\N	4	\N	2025-04-22 10:38:08.199832	2025-04-22 10:38:08.199837	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
191	8109	2334132780	FAISAL HAIDAR MUBARAK MUSTAFA	0545397237	None@n.com	courier	active	Qassim	DHL	3	\N	2025-04-22 10:24:40.293877	2025-04-23 10:39:30.663047	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
189	8803	2512445616	MOHAMED AHMED MOHAMED ELHUSSEINI	0567567726	None@n.com	COURIER	active	QASSIM 	DHL	3	2023-12-14	2025-04-22 10:20:08.731969	2025-04-23 10:41:28.561097	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
209	80052	2571312541	MD OHAB ALI 	0500367873	None@n.com	موظف	active	Hail - HUB	None	4	\N	2025-04-22 10:38:08.467226	2025-06-02 14:56:25.802014	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
198	5213   	2478038306	EMAD AKASH GADAL ELNOUR 	05xxxxxxxx	None@n.com	موظف	active	Qasim	None	4	\N	2025-04-22 10:38:05.55149	2025-04-28 08:52:40.488737	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
201	8807	  2515488746      	MUAZZAM ALI SAGHIR HUSSAIN	05xxxxxxxx	None@n.com	موظف	active	Qasim	None	4	\N	2025-04-22 10:38:06.341351	2025-04-28 08:53:15.245418	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
204	8991    	2486812155     	Naveedullah Ghazi Marjan	05xxxxxxxx	None@n.com	موظف	active	Qasim	None	4	\N	2025-04-22 10:38:07.141516	2025-04-28 08:53:46.707517	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
181	4279.0	2441603038.0	SAIF UL REHMAN  MUHAMMAD IRSHADA	593214415	4279.0@g.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:17.446705	2025-06-07 18:42:48.808216	\N	foreign	0	f	uploads/employees/4279.0_profile_20250607_184248.jpg	\N	\N	1	\N	\N	\N	\N
225	8761	2529580017	MUHAMMAD YOUSAF GUL RAHIM	0555555555	None@n.com	Heavy Driver	active	Qassim	FLOW	4	2025-05-08	2025-05-12 12:17:25.931446	2025-05-12 12:17:25.931449	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
226	50918	2582508640	MOHAMMED DAMAL FAQIR HUSSAIN	592738570	None@n.com	courier	active	Qassim	Aramex	1	\N	2025-05-13 22:15:16.001338	2025-05-13 22:15:16.001341	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
227	50835	2539476297	MOHAMED MUBARK YOUSIF ELAMIN	545592624	None@n.com	courier	active	Qassim	Aramex	1	\N	2025-05-14 07:57:35.49182	2025-05-14 07:57:35.491827	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
211	50306    	    2601216662	MOHAMMED HRIDOY	0572032512	None@n.com	LABOR	inactive	Hail - HUB	FLOW	4	\N	2025-04-22 10:38:08.993715	2025-05-17 10:14:09.971107	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
229	50657	2586530467	SAMER ALI YAHYA ALI ALFUTIAI	0592738570	2586530467@r.com	courier	inactive	Qassim	Aramex	1	\N	2025-05-17 11:17:21.429255	2025-05-17 11:19:04.078238	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
230	50929	2603389707	SADEK MIA	0545397237	None@n.com	LABOR	active	Hail	FLOW	4	2025-06-01	2025-06-02 14:42:07.098663	2025-06-02 14:42:07.098667	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
231	50930	2603389582	SAGOR MIAH	0545397237	None@n.com	LABOR	active	Hail	FLOW	4	2025-06-01	2025-06-02 14:43:23.771912	2025-06-02 14:43:23.771915	\N	foreign	0	f	\N	\N	\N	1	\N	\N	\N	\N
232	1	2586644896	MD YOUSUB ALI	0550764583	None@n.com	LABOR	active	Hail	FLOW	\N	2025-06-01	2025-06-02 14:45:29.688679	2025-07-06 12:06:21.562308	\N	foreign	0	f	\N	\N	\N	1	876543	30	Expired	Suspended
179	4298	2489682019	OMAR ABDULWAHAB MOHS AL MAGHREBI	593214434	4298@h.com	courier	active	Qassim	Aramex	1	\N	2025-04-21 16:56:16.67324	2025-07-06 13:31:11.630873	\N	foreign	0	f	uploads/employees/4298.0_profile_20250529_122536.jpg	uploads/employees/4298.0_national_id_20250529_122934.jpg	uploads/employees/4298.0_license_20250529_123009.jpg	1	0506976824	13	Active	Valid
224	8352	2290833975	EISSA ALI  ABDOULLH MOHAMMED	0558619232	i.ali@rassaudi.com	Project Supervisor	active	QASSIM 	Project Supervisor	6	\N	2025-04-23 12:53:38.630378	2025-07-08 21:00:29.087556	\N	foreign	0	f	\N	\N	\N	1		\N		
\.


--
-- Data for Name: employee_departments; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.employee_departments (employee_id, department_id) FROM stdin;
232	1
186	2
179	1
175	1
178	1
180	1
173	1
172	1
171	1
210	1
182	1
214	1
212	1
174	1
177	1
169	1
176	1
184	1
185	1
187	1
188	1
183	1
193	1
194	1
216	1
217	1
218	1
219	1
220	5
223	6
224	6
\.


--
-- Data for Name: external_authorization; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.external_authorization (id, vehicle_id, employee_id, project_id, authorization_type, status, file_path, external_link, notes, created_at, updated_at, project_name, city) FROM stdin;
2	23	179	2	استلام السيارة من مندوب	approved	\N	\N	في انتظار الموافقة	\N	2025-07-08 14:01:47.829191	\N	\N
3	23	178	\N	استلام السيارة من مندوب	approved	WhatsApp_Image_2025-07-06_at_18.57.35_a014f68a.jpg	https://acrobat.adobe.com/id/urn:aaid:sc:AP:4243d4fc-2215-41e9-9666-572412c4e2d3	hlkhlhl	2025-07-08 13:43:28.665453	2025-07-08 15:55:03.587946	Suleiman Al Habib	
5	23	210	\N	استلام السيارة من مندوب	approved	static/uploads/authorizations/20250708_162029_17519916126346608829605105010398.jpg	https://acrobat.adobe.com/id/urn:aaid:sc:AP:4243d4fc-2215-41e9-9666-572412c4e2d3	نؤنؤنءنس	2025-07-08 16:20:29.732748	2025-07-08 16:45:52.86517	نينينينث	المدينة المنورة
4	23	175	\N	تفويض تسليم	approved	\N	https://acrobat.adobe.com/id/urn:aaid:sc:AP:4243d4fc-2215-41e9-9666-572412c4e2d3	زينينين	2025-07-08 16:15:17.759787	2025-07-08 16:55:51.67349		المدينة المنورة
6	14	173	\N	استلام السيارة من مندوب	approved	\N	https://acrobat.adobe.com/id/urn:aaid:sc:AP:be7e16aa-675c-4592-96ee-1751d8b00192		2025-07-08 18:19:12.062279	2025-07-08 18:20:54.50655		بريدة
7	14	182	\N	تفويض تسليم	approved	\N	https://acrobat.adobe.com/id/urn:aaid:sc:AP:3a37dc73-991a-4498-ab99-835c6130719a		2025-07-08 18:25:09.729837	2025-07-08 18:27:21.675891	ارمكس	بريدة
8	17	179	\N	تفويض تسليم	approved	\N	https://acrobat.adobe.com/id/urn:aaid:sc:AP:ace15cb7-311d-48f8-8eef-06eca8c6fb39		2025-07-08 19:06:25.732135	2025-07-08 19:10:32.985645	ارامكس	بريدة
9	17	179	\N	تفويض تسليم	approved	\N	https://acrobat.adobe.com/id/urn:aaid:sc:AP:ace15cb7-311d-48f8-8eef-06eca8c6fb39		2025-07-08 19:31:52.223749	2025-07-08 19:32:05.846079	Aramex Coruer	بريدة
10	21	183	\N	تفويض تسليم	approved	\N	https://acrobat.adobe.com/id/urn:aaid:sc:AP:70005a2d-7b1e-46a4-87c0-bfdf8975f4fc	استلام السيارة 7277   بديل عن   3943	2025-07-08 19:43:05.186518	2025-07-08 19:52:25.107116	Aramex Coruer	حائل
\.


--
-- Data for Name: external_authorizations; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.external_authorizations (id, vehicle_id, driver_name, driver_phone, project_name, city, authorization_type, duration, authorization_form_link, external_reference, file_path, notes, status, created_by, approved_by, approved_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: fee; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.fee (id, fee_type, description, amount, due_date, is_paid, paid_date, recipient, reference_number, notes, created_at, updated_at, employee_id, document_id, vehicle_id) FROM stdin;
\.


--
-- Data for Name: fees_cost; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.fees_cost (id, document_id, document_type, passport_fee, labor_office_fee, insurance_fee, social_insurance_fee, transfer_sponsorship, due_date, payment_status, payment_date, notes, created_at, updated_at) FROM stdin;
3	26	national_id	750	1600	500	300	f	2025-05-25	pending	\N		2025-04-25 18:51:38.762511	2025-04-25 18:51:38.762514
\.


--
-- Data for Name: government_fee; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.government_fee (id, employee_id, fee_type, fee_date, due_date, amount, payment_status, payment_date, is_automatic, insurance_level, has_national_balance, receipt_number, document_id, transfer_number, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: nationalities; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.nationalities (id, name_ar, name_en, country_code) FROM stdin;
1	سعودي	Saudi	SAU
2	مصري	Egyptian	EGY
3	إماراتي	Emirati	UAE
4	كويتي	Kuwaiti	KWT
5	قطري	Qatari	QAT
6	بحريني	Bahraini	BHR
7	عماني	Omani	OMN
8	أردني	Jordanian	JOR
9	لبناني	Lebanese	LBN
10	سوري	Syrian	SYR
11	عراقي	Iraqi	IRQ
12	فلسطيني	Palestinian	PSE
13	يمني	Yemeni	YEM
14	ليبي	Libyan	LBY
15	تونسي	Tunisian	TUN
16	جزائري	Algerian	DZA
17	مغربي	Moroccan	MAR
18	سوداني	Sudanese	SDN
19	صومالي	Somali	SOM
20	جيبوتي	Djiboutian	DJI
21	أمريكي	American	USA
22	بريطاني	British	GBR
23	فرنسي	French	FRA
24	ألماني	German	DEU
25	إيطالي	Italian	ITA
26	إسباني	Spanish	ESP
27	روسي	Russian	RUS
28	صيني	Chinese	CHN
29	ياباني	Japanese	JPN
30	كوري	Korean	KOR
31	هندي	Indian	IND
32	باكستاني	Pakistani	PAK
33	بنغلاديشي	Bangladeshi	BGD
34	فلبيني	Filipino	PHL
35	إندونيسي	Indonesian	IDN
36	ماليزي	Malaysian	MYS
37	تايلاندي	Thai	THA
38	كندي	Canadian	CAN
39	أسترالي	Australian	AUS
40	برازيلي	Brazilian	BRA
41	أرجنتيني	Argentinian	ARG
42	مكسيكي	Mexican	MEX
43	نيجيري	Nigerian	NGA
44	كيني	Kenyan	KEN
45	جنوب أفريقي	South African	ZAF
46	أثيوبي	Ethiopian	ETH
47	غاني	Ghanaian	GHA
48	أفغاني	Afghan	AFG
49	إيراني	Iranian	IRN
50	تركي	Turkish	TUR
\.


--
-- Data for Name: project; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.project (id, name, description, created_at) FROM stdin;
1	مشروع الرياض	مشروع تطوير العاصمة الرياض	\N
2	مشروع جدة	مشروع تطوير مدينة جدة	\N
3	مشروع المنطقة الشرقية	مشروع تطوير المنطقة الشرقية	\N
4	مشروع نيوم	مشروع مدينة نيوم المستقبلية	\N
5	مشروع القصيم	مشروع تطوير منطقة القصيم	\N
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.projects (id, name, description, location, start_date, end_date, status, manager_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: renewal_fee; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.renewal_fee (id, document_id, fee_date, fee_type, amount, payment_status, payment_date, receipt_number, notes, created_at, updated_at, transfer_number) FROM stdin;
\.


--
-- Data for Name: salary; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.salary (id, employee_id, month, year, basic_salary, allowances, deductions, bonus, net_salary, notes, created_at, updated_at, company_id) FROM stdin;
51	179	3	2025	2500	300	0	0	2800	None	2025-04-21 17:35:34.902534	2025-04-21 18:10:21.120788	1
52	181	3	2025	2500	300	0	0	2800	None	2025-04-21 17:35:35.736296	2025-04-21 18:11:03.8433	1
43	180	3	2025	2500	300	0	0	2800	None	2025-04-21 17:34:41.140186	2025-04-21 18:05:29.824914	1
45	173	3	2025	2500	300	0	0	2800	None	2025-04-21 17:35:31.674709	2025-04-21 18:06:18.360291	1
46	174	3	2025	2500	300	383	0	2417	None	2025-04-21 17:35:32.218264	2025-04-21 18:07:12.036516	1
47	175	3	2025	2500	300	0	0	2800	None	2025-04-21 17:35:32.754893	2025-04-21 18:07:44.343695	1
48	176	3	2025	2500	300	1300	0	1500	دوام من يوم 15-3-2025	2025-04-21 17:35:33.290249	2025-04-21 18:08:43.122816	1
49	177	3	2025	2500	300	0	0	2800	None	2025-04-21 17:35:33.831895	2025-04-21 18:09:05.564204	1
50	178	3	2025	2500	300	0	0	2800	None	2025-04-21 17:35:34.367283	2025-04-21 18:09:57.832804	1
53	182	3	2025	2500	300	0	0	2800	None	2025-04-21 17:35:36.274057	2025-04-21 18:11:38.073647	1
54	183	3	2025	2500	300	549	0	2251	None	2025-04-21 17:35:36.811347	2025-04-21 18:12:50.569362	1
44	172	3	2025	2500	300	850	0	1950	يوجد خصم قيمة شحنة 850	2025-04-21 17:35:31.119491	2025-04-21 18:13:28.589784	1
55	184	3	2025	1300	0	0	873	2173		2025-04-22 11:08:37.719348	2025-04-22 11:08:37.719353	1
56	185	3	2025	1300	0	0	873	2173		2025-04-22 11:08:38.07223	2025-04-22 11:08:38.072234	1
57	186	3	2025	1300	0	0	873	2173		2025-04-22 11:08:39.15619	2025-04-22 11:08:39.156196	1
58	187	3	2025	1300	0	0	873	2173		2025-04-22 11:08:39.749647	2025-04-22 11:08:39.749652	1
59	188	3	2025	1300	0	0	873	2173		2025-04-22 11:08:40.788931	2025-04-22 11:08:40.788936	1
60	222	3	2025	1300	0	0	715	2015		2025-04-22 11:11:03.989754	2025-04-22 11:11:03.989758	1
61	221	3	2025	1300	0	0	715	2015		2025-04-22 11:11:05.050818	2025-04-22 11:11:05.050823	1
62	220	3	2025	1300	0	0	715	2015		2025-04-22 11:11:06.342195	2025-04-22 11:11:06.3422	1
63	219	3	2025	1300	0	0	715	2015		2025-04-22 11:11:07.611727	2025-04-22 11:11:07.611732	1
64	218	3	2025	1300	0	0	715	2015		2025-04-22 11:11:08.262167	2025-04-22 11:11:08.262172	1
65	217	3	2025	1300	0	0	715	2015		2025-04-22 11:11:08.83388	2025-04-22 11:11:08.833885	1
67	175	4	2025	2500	300	0	300	3100		2025-05-14 18:37:14.06846	2025-05-14 18:38:04.512003	1
66	180	4	2025	2500	300	0	4456	7256		2025-05-14 18:32:21.820428	2025-05-15 04:03:59.390419	1
68	181	4	2025	2500	300	0	2943	5743		2025-05-15 04:27:22.552302	2025-05-15 04:27:22.552309	1
70	183	4	2025	2500	300	1000	2046	3846	خصم 1000ريال قيمة حادث مروري والمتبقي1000ريال على راتب شهر 5-2025	2025-05-15 04:33:52.188094	2025-05-15 04:33:52.188098	1
71	177	4	2025	2500	300	0	2000	4800		2025-05-15 04:36:16.007437	2025-05-15 04:36:16.007441	1
73	169	4	2025	2500	300	0	715	3515		2025-05-15 04:40:43.096447	2025-05-15 04:40:43.096451	1
75	173	4	2025	2500	300	0	2527	5327		2025-05-15 04:46:28.756311	2025-05-15 04:46:28.756316	1
76	176	4	2025	2500	300	0	283	3083		2025-05-15 04:49:30.948041	2025-05-15 04:49:30.948062	1
77	174	4	2025	2500	300	0	2409	5209		2025-05-15 04:51:09.007654	2025-05-15 04:51:09.007659	1
78	178	4	2025	2500	300	0	100	2900		2025-05-15 05:04:26.586014	2025-05-15 05:04:26.586018	1
79	179	4	2025	2500	300	0	1100	3900		2025-05-15 05:05:20.262004	2025-05-15 05:05:20.262008	1
80	171	4	2025	2500	300	0	3300	6100		2025-05-15 05:26:38.116384	2025-05-15 05:26:38.116389	1
74	172	4	2025	2500	300	2000	2243	3043	خصم 2000 ريال قيمة حادث مروري 	2025-05-15 04:44:02.790757	2025-05-15 05:44:12.122984	1
81	182	4	2025	2500	300	0	2400	5200		2025-05-15 06:20:01.937074	2025-05-15 06:20:01.937079	1
82	188	4	2025	1300	0	0	151	1451		2025-05-18 16:16:09.054532	2025-05-18 16:16:09.054536	1
83	187	4	2025	1300	0	0	151	1451		2025-05-18 16:16:09.511112	2025-05-18 16:16:09.511117	1
84	186	4	2025	1300	0	0	151	1451		2025-05-18 16:16:09.859241	2025-05-18 16:16:09.859246	1
85	185	4	2025	1300	0	0	151	1451		2025-05-18 16:16:10.225024	2025-05-18 16:16:10.225028	1
86	184	4	2025	1300	0	0	151	1451		2025-05-18 16:16:10.580132	2025-05-18 16:16:10.580137	1
93	179	5	2025	2500	0	0	300	2800		2025-06-21 11:12:42.216196	2025-06-21 11:12:42.216201	\N
94	181	5	2025	2500	0	0	300	2800		2025-06-21 11:12:42.95528	2025-06-21 11:12:42.955285	\N
95	183	5	2025	2500	0	0	300	2800		2025-06-21 11:12:43.590987	2025-06-21 11:12:43.590991	\N
97	177	5	2025	2500	0	0	300	2800		2025-06-21 11:12:45.202171	2025-06-21 11:12:45.202176	\N
98	174	5	2025	2500	0	0	300	2800		2025-06-21 11:12:46.312097	2025-06-21 11:12:46.312102	\N
101	173	5	2025	2500	0	0	300	2800		2025-06-21 11:12:48.486896	2025-06-21 11:12:48.486901	\N
102	182	5	2025	2500	0	0	300	2800		2025-06-21 11:12:49.751508	2025-06-21 11:12:49.751513	\N
103	180	5	2025	2500	0	0	300	2800		2025-06-21 11:12:50.8507	2025-06-21 11:12:50.850705	\N
104	178	5	2025	2500	0	0	300	2800		2025-06-21 11:12:51.386813	2025-06-21 11:12:51.386818	\N
105	175	5	2025	2500	0	0	300	2800		2025-06-21 11:12:52.48708	2025-06-21 11:12:52.487084	\N
107	176	5	2025	2500	0	0	300	2800		2025-06-21 11:20:00.368547	2025-06-21 11:20:00.368552	\N
108	226	5	2025	2500	0	0	300	2800		2025-06-21 11:22:04.300757	2025-06-21 11:22:17.905204	\N
99	171	5	2025	2500	0	0	300	2800		2025-06-21 11:12:46.955621	2025-06-21 11:31:09.08577	\N
100	172	5	2025	2500	0	0	300	2800		2025-06-21 11:12:48.121179	2025-06-21 11:34:22.555167	\N
96	169	5	2025	2500	0	0	300	2800		2025-06-21 11:12:44.722556	2025-06-21 11:34:37.404209	\N
109	184	5	2025	1300	0	0	0	1300		2025-06-21 11:40:10.623351	2025-06-21 11:40:10.623355	\N
110	185	5	2025	1300	0	0	0	1300		2025-06-21 11:40:11.029742	2025-06-21 11:40:11.029746	\N
111	186	5	2025	1300	0	0	0	1300		2025-06-21 11:40:11.393948	2025-06-21 11:40:11.393952	\N
112	187	5	2025	1300	0	0	0	1300		2025-06-21 11:40:11.767671	2025-06-21 11:40:11.767676	\N
113	188	5	2025	1300	0	0	0	1300		2025-06-21 11:40:12.922127	2025-06-21 11:40:12.922132	\N
114	216	5	2025	1300	0	0	0	1300		2025-06-21 11:41:23.403419	2025-06-21 11:41:23.403423	\N
115	217	5	2025	1300	0	0	0	1300		2025-06-21 11:41:24.531926	2025-06-21 11:41:24.531931	\N
116	218	5	2025	1300	0	0	0	1300		2025-06-21 11:41:24.903427	2025-06-21 11:41:24.903432	\N
117	219	5	2025	1300	0	0	0	1300		2025-06-21 11:41:26.031585	2025-06-21 11:41:26.03159	\N
118	220	5	2025	1300	0	0	0	1300		2025-06-21 11:41:26.540035	2025-06-21 11:41:26.54004	\N
119	221	5	2025	1300	0	0	0	1300		2025-06-21 11:41:27.679344	2025-06-21 11:41:27.679349	\N
120	222	5	2025	1300	0	0	0	1300		2025-06-21 11:41:28.24577	2025-06-21 11:41:28.245775	\N
\.


--
-- Data for Name: subscription_notifications; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.subscription_notifications (id, company_id, notification_type, title, message, is_read, is_urgent, sent_date, expires_at, created_at) FROM stdin;
\.


--
-- Data for Name: system_audit; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.system_audit (id, action, entity_type, entity_id, entity_name, previous_data, new_data, details, ip_address, "timestamp", user_id) FROM stdin;
1392	access_denied	departments	0	Unknown	\N	\N	محاولة وصول مرفوضة إلى الأقسام	37.217.168.153	2025-06-20 22:41:54.120016	\N
1393	export	employee_basic_report	175	\N	\N	\N	تم تصدير التقرير الأساسي المصمم للموظف: MOHAMMED MOQBEL M. ABDULLAH GHANEM مع الصور	\N	2025-06-20 23:38:16.92814	\N
1394	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-14 إلى 2025-06-20	34.60.193.23	2025-06-20 23:40:51.036979	\N
1395	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-14 إلى 2025-06-20	34.60.193.23	2025-06-20 23:40:58.055803	\N
1396	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-14 إلى 2025-06-20	34.60.193.23	2025-06-20 23:41:00.371486	\N
1397	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-14 إلى 2025-06-20	34.60.193.23	2025-06-20 23:41:08.276683	\N
1398	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-14 إلى 2025-06-20	34.60.193.23	2025-06-20 23:41:11.525184	\N
1399	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-14 إلى 2025-06-20	34.60.193.23	2025-06-20 23:41:12.690239	\N
1400	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-21 إلى 2025-06-21	35.188.87.224	2025-06-21 09:38:07.175698	\N
1401	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-21 إلى 2025-06-21	35.188.87.224	2025-06-21 09:38:08.808687	\N
1402	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-21 إلى 2025-06-21	35.188.87.224	2025-06-21 09:38:09.552938	\N
1403	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-21 إلى 2025-06-21	35.188.87.224	2025-06-21 09:38:11.530939	\N
1404	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-21 إلى 2025-06-21	35.188.87.224	2025-06-21 09:38:12.45298	\N
1405	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-21 إلى 2025-06-21	35.188.87.224	2025-06-21 09:38:12.931928	\N
1406	create	salary	178	\N	\N	\N	تم إنشاء سجل راتب للموظف: SHABEER MULLA PALLI لشهر 5/2025	\N	2025-06-21 11:04:28.284015	\N
1407	create	salary	180	\N	\N	\N	تم إنشاء سجل راتب للموظف: HUSSAM AL DAIN لشهر 5/2025	\N	2025-06-21 11:04:29.424994	\N
1408	create	salary	182	\N	\N	\N	تم إنشاء سجل راتب للموظف: MUHAMMAD USMAN MUHAMMAD MAQBOOL لشهر 5/2025	\N	2025-06-21 11:04:30.850133	\N
1409	create	salary	173	\N	\N	\N	تم إنشاء سجل راتب للموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI لشهر 5/2025	\N	2025-06-21 11:04:31.561137	\N
1410	create	salary	172	\N	\N	\N	تم إنشاء سجل راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:04:32.763594	\N
1411	create	salary	171	\N	\N	\N	تم إنشاء سجل راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:04:34.050782	\N
1412	export	salary	0	\N	\N	\N	تم تصدير 46 سجل راتب إلى ملف Excel [جميع الشهور - جميع السنوات - جميع الأقسام]	\N	2025-06-21 11:05:18.568266	\N
1413	delete	salary	87	\N	\N	\N	تم حذف سجل راتب للموظف: SHABEER MULLA PALLI لشهر 5/2025	\N	2025-06-21 11:09:22.609868	\N
1414	delete	salary	88	\N	\N	\N	تم حذف سجل راتب للموظف: HUSSAM AL DAIN لشهر 5/2025	\N	2025-06-21 11:09:35.245624	\N
1415	delete	salary	89	\N	\N	\N	تم حذف سجل راتب للموظف: MUHAMMAD USMAN MUHAMMAD MAQBOOL لشهر 5/2025	\N	2025-06-21 11:09:45.007953	\N
1416	delete	salary	90	\N	\N	\N	تم حذف سجل راتب للموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI لشهر 5/2025	\N	2025-06-21 11:09:55.093874	\N
1417	delete	salary	91	\N	\N	\N	تم حذف سجل راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:10:05.821421	\N
1418	delete	salary	92	\N	\N	\N	تم حذف سجل راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:10:16.483467	\N
1419	create	salary	179	\N	\N	\N	تم إنشاء سجل راتب للموظف: OMAR ABDULWAHAB MOHS AL MAGHREBI لشهر 5/2025	\N	2025-06-21 11:12:42.330285	\N
1420	create	salary	181	\N	\N	\N	تم إنشاء سجل راتب للموظف: SAIF UL REHMAN  MUHAMMAD IRSHADA لشهر 5/2025	\N	2025-06-21 11:12:43.043618	\N
1421	create	salary	183	\N	\N	\N	تم إنشاء سجل راتب للموظف: ‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI لشهر 5/2025	\N	2025-06-21 11:12:43.680373	\N
1422	create	salary	169	\N	\N	\N	تم إنشاء سجل راتب للموظف: ‏SALEH NASSER YASLAM BAANS لشهر 5/2025	\N	2025-06-21 11:12:44.814839	\N
1423	create	salary	177	\N	\N	\N	تم إنشاء سجل راتب للموظف: TAHIR ALI MEHBOOB ALI لشهر 5/2025	\N	2025-06-21 11:12:45.293497	\N
1424	create	salary	174	\N	\N	\N	تم إنشاء سجل راتب للموظف: ABBAS AMEEN QAID QASEM لشهر 5/2025	\N	2025-06-21 11:12:46.3995	\N
1425	create	salary	171	\N	\N	\N	تم إنشاء سجل راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:12:47.042653	\N
1426	create	salary	172	\N	\N	\N	تم إنشاء سجل راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:12:48.213534	\N
1427	create	salary	173	\N	\N	\N	تم إنشاء سجل راتب للموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI لشهر 5/2025	\N	2025-06-21 11:12:48.573554	\N
1428	create	salary	182	\N	\N	\N	تم إنشاء سجل راتب للموظف: MUHAMMAD USMAN MUHAMMAD MAQBOOL لشهر 5/2025	\N	2025-06-21 11:12:49.838249	\N
1429	create	salary	180	\N	\N	\N	تم إنشاء سجل راتب للموظف: HUSSAM AL DAIN لشهر 5/2025	\N	2025-06-21 11:12:50.937679	\N
1430	create	salary	178	\N	\N	\N	تم إنشاء سجل راتب للموظف: SHABEER MULLA PALLI لشهر 5/2025	\N	2025-06-21 11:12:51.493366	\N
1431	create	salary	175	\N	\N	\N	تم إنشاء سجل راتب للموظف: MOHAMMED MOQBEL M. ABDULLAH GHANEM لشهر 5/2025	\N	2025-06-21 11:12:52.573902	\N
1432	create	salary	176	\N	\N	\N	تم إنشاء سجل راتب للموظف: MOHAMED MUBARK YOUSIF ELAMIN لشهر 6/2025	\N	2025-06-21 11:17:41.915159	\N
1433	create	salary	176	\N	\N	\N	تم إنشاء سجل راتب للموظف: MOHAMED MUBARK YOUSIF ELAMIN لشهر 5/2025	\N	2025-06-21 11:20:00.455715	\N
1434	create	salary	226	\N	\N	\N	تم إنشاء سجل راتب للموظف: MOHAMMED DAMAL FAQIR HUSSAIN لشهر 6/2025	\N	2025-06-21 11:22:04.388735	\N
1435	update	salary	108	\N	\N	\N	تم تعديل سجل راتب للموظف: MOHAMMED DAMAL FAQIR HUSSAIN لشهر 5/2025	\N	2025-06-21 11:22:17.998236	\N
1436	share_whatsapp_link	salary	93	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: OMAR ABDULWAHAB MOHS AL MAGHREBI لشهر 5/2025	\N	2025-06-21 11:22:46.565638	\N
1437	generate_notification	salary	93	\N	\N	\N	تم إنشاء إشعار راتب للموظف: OMAR ABDULWAHAB MOHS AL MAGHREBI لشهر 5/2025	\N	2025-06-21 11:23:02.023818	\N
1438	generate_notification	salary	93	\N	\N	\N	تم إنشاء إشعار راتب للموظف: OMAR ABDULWAHAB MOHS AL MAGHREBI لشهر 5/2025	\N	2025-06-21 11:23:05.134939	\N
1439	generate_notification	salary	93	\N	\N	\N	تم إنشاء إشعار راتب للموظف: OMAR ABDULWAHAB MOHS AL MAGHREBI لشهر 5/2025	\N	2025-06-21 11:23:08.203787	\N
1440	generate_notification	salary	93	\N	\N	\N	تم إنشاء إشعار راتب للموظف: OMAR ABDULWAHAB MOHS AL MAGHREBI لشهر 5/2025	\N	2025-06-21 11:23:11.274718	\N
1441	generate_notification	salary	93	\N	\N	\N	تم إنشاء إشعار راتب للموظف: OMAR ABDULWAHAB MOHS AL MAGHREBI لشهر 5/2025	\N	2025-06-21 11:23:14.326337	\N
1442	share_whatsapp_link	salary	94	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: SAIF UL REHMAN  MUHAMMAD IRSHADA لشهر 5/2025	\N	2025-06-21 11:23:34.141158	\N
1443	generate_notification	salary	94	\N	\N	\N	تم إنشاء إشعار راتب للموظف: SAIF UL REHMAN  MUHAMMAD IRSHADA لشهر 5/2025	\N	2025-06-21 11:23:39.369675	\N
1444	generate_notification	salary	94	\N	\N	\N	تم إنشاء إشعار راتب للموظف: SAIF UL REHMAN  MUHAMMAD IRSHADA لشهر 5/2025	\N	2025-06-21 11:23:42.425809	\N
1445	generate_notification	salary	94	\N	\N	\N	تم إنشاء إشعار راتب للموظف: SAIF UL REHMAN  MUHAMMAD IRSHADA لشهر 5/2025	\N	2025-06-21 11:23:45.501478	\N
1446	generate_notification	salary	94	\N	\N	\N	تم إنشاء إشعار راتب للموظف: SAIF UL REHMAN  MUHAMMAD IRSHADA لشهر 5/2025	\N	2025-06-21 11:23:48.548618	\N
1447	share_whatsapp_link	salary	95	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: ‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI لشهر 5/2025	\N	2025-06-21 11:23:49.145579	\N
1448	generate_notification	salary	95	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI لشهر 5/2025	\N	2025-06-21 11:23:54.247567	\N
1449	generate_notification	salary	95	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI لشهر 5/2025	\N	2025-06-21 11:23:57.253481	\N
1450	generate_notification	salary	95	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI لشهر 5/2025	\N	2025-06-21 11:24:00.249185	\N
1451	generate_notification	salary	95	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI لشهر 5/2025	\N	2025-06-21 11:24:03.462803	\N
1452	share_whatsapp_link	salary	96	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: ‏SALEH NASSER YASLAM BAANS لشهر 5/2025	\N	2025-06-21 11:24:05.304892	\N
1453	generate_notification	salary	96	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏SALEH NASSER YASLAM BAANS لشهر 5/2025	\N	2025-06-21 11:24:10.548968	\N
1454	generate_notification	salary	96	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏SALEH NASSER YASLAM BAANS لشهر 5/2025	\N	2025-06-21 11:24:13.645139	\N
1455	generate_notification	salary	96	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏SALEH NASSER YASLAM BAANS لشهر 5/2025	\N	2025-06-21 11:24:16.679272	\N
1456	generate_notification	salary	96	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏SALEH NASSER YASLAM BAANS لشهر 5/2025	\N	2025-06-21 11:24:19.834028	\N
1457	share_whatsapp_link	salary	97	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: TAHIR ALI MEHBOOB ALI لشهر 5/2025	\N	2025-06-21 11:24:21.025259	\N
1458	generate_notification	salary	94	\N	\N	\N	تم إنشاء إشعار راتب للموظف: SAIF UL REHMAN  MUHAMMAD IRSHADA لشهر 5/2025	\N	2025-06-21 11:24:24.383782	\N
1459	generate_notification	salary	95	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI لشهر 5/2025	\N	2025-06-21 11:24:27.469439	\N
1460	generate_notification	salary	97	\N	\N	\N	تم إنشاء إشعار راتب للموظف: TAHIR ALI MEHBOOB ALI لشهر 5/2025	\N	2025-06-21 11:24:30.4743	\N
1461	generate_notification	salary	97	\N	\N	\N	تم إنشاء إشعار راتب للموظف: TAHIR ALI MEHBOOB ALI لشهر 5/2025	\N	2025-06-21 11:24:33.523818	\N
1462	generate_notification	salary	97	\N	\N	\N	تم إنشاء إشعار راتب للموظف: TAHIR ALI MEHBOOB ALI لشهر 5/2025	\N	2025-06-21 11:24:36.589788	\N
1463	generate_notification	salary	97	\N	\N	\N	تم إنشاء إشعار راتب للموظف: TAHIR ALI MEHBOOB ALI لشهر 5/2025	\N	2025-06-21 11:24:39.632342	\N
1464	share_whatsapp_link	salary	97	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: TAHIR ALI MEHBOOB ALI لشهر 5/2025	\N	2025-06-21 11:24:40.196779	\N
1465	generate_notification	salary	94	\N	\N	\N	تم إنشاء إشعار راتب للموظف: SAIF UL REHMAN  MUHAMMAD IRSHADA لشهر 5/2025	\N	2025-06-21 11:24:43.128972	\N
1466	generate_notification	salary	97	\N	\N	\N	تم إنشاء إشعار راتب للموظف: TAHIR ALI MEHBOOB ALI لشهر 5/2025	\N	2025-06-21 11:24:46.279067	\N
1467	share_whatsapp_link	salary	98	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: ABBAS AMEEN QAID QASEM لشهر 5/2025	\N	2025-06-21 11:25:05.279912	\N
1468	generate_notification	salary	98	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ABBAS AMEEN QAID QASEM لشهر 5/2025	\N	2025-06-21 11:25:10.501559	\N
1469	generate_notification	salary	98	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ABBAS AMEEN QAID QASEM لشهر 5/2025	\N	2025-06-21 11:25:13.506803	\N
1470	generate_notification	salary	98	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ABBAS AMEEN QAID QASEM لشهر 5/2025	\N	2025-06-21 11:25:16.469821	\N
1471	generate_notification	salary	98	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ABBAS AMEEN QAID QASEM لشهر 5/2025	\N	2025-06-21 11:25:19.44232	\N
1472	share_whatsapp_link	salary	99	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:25:20.005046	\N
1473	generate_notification	salary	99	\N	\N	\N	تم إنشاء إشعار راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:25:24.763359	\N
1474	generate_notification	salary	99	\N	\N	\N	تم إنشاء إشعار راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:25:27.74373	\N
1475	generate_notification	salary	99	\N	\N	\N	تم إنشاء إشعار راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:25:30.739795	\N
1476	generate_notification	salary	99	\N	\N	\N	تم إنشاء إشعار راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:25:33.669587	\N
1477	share_whatsapp_link	salary	100	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:25:34.239171	\N
1478	generate_notification	salary	100	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:25:39.414095	\N
1479	generate_notification	salary	100	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:25:42.395254	\N
1480	generate_notification	salary	100	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:25:45.437744	\N
1481	generate_notification	salary	100	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:25:48.445286	\N
1482	share_whatsapp_link	salary	101	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI لشهر 5/2025	\N	2025-06-21 11:25:51.335215	\N
1483	share_whatsapp_link	salary	101	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI لشهر 5/2025	\N	2025-06-21 11:25:51.852075	\N
1484	share_whatsapp_link	salary	101	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI لشهر 5/2025	\N	2025-06-21 11:28:17.355174	\N
1485	generate_notification	salary	101	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI لشهر 5/2025	\N	2025-06-21 11:28:29.379085	\N
1486	generate_notification	salary	101	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI لشهر 5/2025	\N	2025-06-21 11:28:32.529575	\N
1487	generate_notification	salary	101	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI لشهر 5/2025	\N	2025-06-21 11:28:35.591831	\N
1488	generate_notification	salary	101	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMMED IMRAN SHOUKAT ALI SHOUKAT ALI لشهر 5/2025	\N	2025-06-21 11:28:38.628003	\N
1489	share_whatsapp_link	salary	102	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: MUHAMMAD USMAN MUHAMMAD MAQBOOL لشهر 5/2025	\N	2025-06-21 11:29:05.375096	\N
1490	generate_notification	salary	102	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MUHAMMAD USMAN MUHAMMAD MAQBOOL لشهر 5/2025	\N	2025-06-21 11:29:10.300732	\N
1491	generate_notification	salary	102	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MUHAMMAD USMAN MUHAMMAD MAQBOOL لشهر 5/2025	\N	2025-06-21 11:29:13.864951	\N
1492	generate_notification	salary	102	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MUHAMMAD USMAN MUHAMMAD MAQBOOL لشهر 5/2025	\N	2025-06-21 11:29:16.906593	\N
1493	generate_notification	salary	102	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MUHAMMAD USMAN MUHAMMAD MAQBOOL لشهر 5/2025	\N	2025-06-21 11:29:19.916497	\N
1494	share_whatsapp_link	salary	103	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: HUSSAM AL DAIN لشهر 5/2025	\N	2025-06-21 11:29:21.990436	\N
1495	generate_notification	salary	103	\N	\N	\N	تم إنشاء إشعار راتب للموظف: HUSSAM AL DAIN لشهر 5/2025	\N	2025-06-21 11:29:26.99308	\N
1496	generate_notification	salary	103	\N	\N	\N	تم إنشاء إشعار راتب للموظف: HUSSAM AL DAIN لشهر 5/2025	\N	2025-06-21 11:29:29.963792	\N
1497	generate_notification	salary	103	\N	\N	\N	تم إنشاء إشعار راتب للموظف: HUSSAM AL DAIN لشهر 5/2025	\N	2025-06-21 11:29:32.877313	\N
1498	generate_notification	salary	103	\N	\N	\N	تم إنشاء إشعار راتب للموظف: HUSSAM AL DAIN لشهر 5/2025	\N	2025-06-21 11:29:35.815131	\N
1499	share_whatsapp_link	salary	104	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: SHABEER MULLA PALLI لشهر 5/2025	\N	2025-06-21 11:29:36.385651	\N
1500	generate_notification	salary	104	\N	\N	\N	تم إنشاء إشعار راتب للموظف: SHABEER MULLA PALLI لشهر 5/2025	\N	2025-06-21 11:29:41.050914	\N
1501	generate_notification	salary	104	\N	\N	\N	تم إنشاء إشعار راتب للموظف: SHABEER MULLA PALLI لشهر 5/2025	\N	2025-06-21 11:29:43.919143	\N
1502	generate_notification	salary	104	\N	\N	\N	تم إنشاء إشعار راتب للموظف: SHABEER MULLA PALLI لشهر 5/2025	\N	2025-06-21 11:29:46.902267	\N
1503	generate_notification	salary	104	\N	\N	\N	تم إنشاء إشعار راتب للموظف: SHABEER MULLA PALLI لشهر 5/2025	\N	2025-06-21 11:29:49.921622	\N
1504	share_whatsapp_link	salary	105	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: MOHAMMED MOQBEL M. ABDULLAH GHANEM لشهر 5/2025	\N	2025-06-21 11:29:52.416106	\N
1505	generate_notification	salary	105	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMMED MOQBEL M. ABDULLAH GHANEM لشهر 5/2025	\N	2025-06-21 11:29:57.730643	\N
1506	generate_notification	salary	105	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMMED MOQBEL M. ABDULLAH GHANEM لشهر 5/2025	\N	2025-06-21 11:30:00.803968	\N
1507	generate_notification	salary	105	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMMED MOQBEL M. ABDULLAH GHANEM لشهر 5/2025	\N	2025-06-21 11:30:04.189982	\N
1508	generate_notification	salary	105	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMMED MOQBEL M. ABDULLAH GHANEM لشهر 5/2025	\N	2025-06-21 11:30:07.155616	\N
1509	share_whatsapp_link	salary	107	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: MOHAMED MUBARK YOUSIF ELAMIN لشهر 5/2025	\N	2025-06-21 11:30:07.722152	\N
1510	generate_notification	salary	107	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMED MUBARK YOUSIF ELAMIN لشهر 5/2025	\N	2025-06-21 11:30:12.873182	\N
1511	generate_notification	salary	107	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMED MUBARK YOUSIF ELAMIN لشهر 5/2025	\N	2025-06-21 11:30:15.785629	\N
1512	generate_notification	salary	107	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMED MUBARK YOUSIF ELAMIN لشهر 5/2025	\N	2025-06-21 11:30:18.664791	\N
1513	generate_notification	salary	107	\N	\N	\N	تم إنشاء إشعار راتب للموظف: MOHAMED MUBARK YOUSIF ELAMIN لشهر 5/2025	\N	2025-06-21 11:30:21.583427	\N
1514	update	salary	99	\N	\N	\N	تم تعديل سجل راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:31:09.172545	\N
1515	share_whatsapp_link	salary	99	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:31:52.372968	\N
1516	generate_notification	salary	99	\N	\N	\N	تم إنشاء إشعار راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:31:58.786475	\N
1517	generate_notification	salary	99	\N	\N	\N	تم إنشاء إشعار راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:32:01.747814	\N
1518	generate_notification	salary	99	\N	\N	\N	تم إنشاء إشعار راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:32:04.638414	\N
1519	generate_notification	salary	99	\N	\N	\N	تم إنشاء إشعار راتب للموظف: WADHAH NABIL QASEM QAID AL TAHERI  لشهر 5/2025	\N	2025-06-21 11:32:07.585924	\N
1520	update	salary	100	\N	\N	\N	تم تعديل سجل راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:34:22.651152	\N
1521	update	salary	96	\N	\N	\N	تم تعديل سجل راتب للموظف: ‏SALEH NASSER YASLAM BAANS لشهر 5/2025	\N	2025-06-21 11:34:37.49116	\N
1522	share_whatsapp_link	salary	100	\N	\N	\N	تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:34:52.397068	\N
1523	generate_notification	salary	100	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:34:58.093397	\N
1524	generate_notification	salary	100	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:35:27.032276	\N
1525	generate_notification	salary	100	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏HASAN MOHAMMED ALI RAGEH‏ لشهر 5/2025	\N	2025-06-21 11:35:35.314568	\N
1526	create	salary	184	\N	\N	\N	تم إنشاء سجل راتب للموظف: MD RABBI لشهر 5/2025	\N	2025-06-21 11:40:10.744265	\N
1527	create	salary	185	\N	\N	\N	تم إنشاء سجل راتب للموظف: NASIR UDDIN لشهر 5/2025	\N	2025-06-21 11:40:11.1201	\N
1528	create	salary	186	\N	\N	\N	تم إنشاء سجل راتب للموظف: SOZAN MIA لشهر 5/2025	\N	2025-06-21 11:40:11.484289	\N
1529	create	salary	187	\N	\N	\N	تم إنشاء سجل راتب للموظف: SHABUDDIN HABIB لشهر 5/2025	\N	2025-06-21 11:40:11.857833	\N
1530	create	salary	188	\N	\N	\N	تم إنشاء سجل راتب للموظف: MD RATAN MIAH MD HOBI لشهر 5/2025	\N	2025-06-21 11:40:13.014388	\N
1531	create	salary	216	\N	\N	\N	تم إنشاء سجل راتب للموظف: ABDULL KYUAM لشهر 5/2025	\N	2025-06-21 11:41:23.493986	\N
1532	create	salary	217	\N	\N	\N	تم إنشاء سجل راتب للموظف: KAZI TOUFIQUL ISLAM لشهر 5/2025	\N	2025-06-21 11:41:24.622237	\N
1533	create	salary	218	\N	\N	\N	تم إنشاء سجل راتب للموظف: MD ESHAQ BANGLADESHI لشهر 5/2025	\N	2025-06-21 11:41:24.994548	\N
1534	create	salary	219	\N	\N	\N	تم إنشاء سجل راتب للموظف: MD MUNZURUL ISLAM لشهر 5/2025	\N	2025-06-21 11:41:26.12264	\N
1535	create	salary	220	\N	\N	\N	تم إنشاء سجل راتب للموظف: MEHEDI KHAN لشهر 5/2025	\N	2025-06-21 11:41:26.630445	\N
1536	create	salary	221	\N	\N	\N	تم إنشاء سجل راتب للموظف: MD SAIFUR RAHMAN MAHEDI لشهر 5/2025	\N	2025-06-21 11:41:27.769698	\N
1537	create	salary	222	\N	\N	\N	تم إنشاء سجل راتب للموظف: RASEL MD لشهر 5/2025	\N	2025-06-21 11:41:28.341151	\N
1538	export	salary	0	\N	\N	\N	تم تصدير 66 سجل راتب إلى ملف Excel [جميع الشهور - جميع السنوات - جميع الأقسام]	\N	2025-06-21 11:42:43.08801	\N
1539	export	salary	0	\N	\N	\N	تم تصدير 66 سجل راتب إلى ملف Excel [جميع الشهور - جميع السنوات - جميع الأقسام]	\N	2025-06-21 11:42:56.506805	\N
1540	delete	salary	106	\N	\N	\N	تم حذف سجل راتب للموظف: MOHAMED MUBARK YOUSIF ELAMIN لشهر 6/2025	\N	2025-06-21 11:43:30.694802	\N
1541	export	salary	0	\N	\N	\N	تم تصدير 26 سجل راتب إلى ملف Excel [شهر: مايو - سنة: 2025 - جميع الأقسام]	\N	2025-06-21 11:43:43.481235	\N
1542	generate_notification	salary	95	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI لشهر 5/2025	\N	2025-06-21 11:49:01.096763	\N
1543	export	salary	0	\N	\N	\N	تم تصدير 0 سجل راتب إلى ملف Excel [شهر: مايو - سنة: 2025 - جميع الأقسام - موظف: MOHAMED MUBARK YOUSIF ELAMIN]	\N	2025-06-21 11:50:51.132775	\N
1544	export	salary	0	\N	\N	\N	تم تصدير 26 سجل راتب إلى ملف Excel [شهر: مايو - سنة: 2025 - جميع الأقسام]	\N	2025-06-21 11:51:29.660983	\N
1545	generate_notification	salary	103	\N	\N	\N	تم إنشاء إشعار راتب للموظف: HUSSAM AL DAIN لشهر 5/2025	\N	2025-06-21 12:15:11.397149	\N
1546	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-23 إلى 2025-06-23	104.154.70.112	2025-06-23 10:35:50.542575	\N
1547	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-23 إلى 2025-06-23	104.154.70.112	2025-06-23 10:35:52.181478	\N
1548	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-23 إلى 2025-06-23	104.154.70.112	2025-06-23 10:35:52.940264	\N
1549	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-23 إلى 2025-06-23	104.154.70.112	2025-06-23 10:35:54.911916	\N
1550	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-23 إلى 2025-06-23	104.154.70.112	2025-06-23 10:35:55.832556	\N
1551	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-23 إلى 2025-06-23	104.154.70.112	2025-06-23 10:35:56.313124	\N
1552	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-17 إلى 2025-06-23	104.154.70.112	2025-06-23 10:40:38.677346	\N
1553	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-17 إلى 2025-06-23	104.154.70.112	2025-06-23 10:40:44.428404	\N
1554	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-17 إلى 2025-06-23	104.154.70.112	2025-06-23 10:40:46.516417	\N
1555	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-17 إلى 2025-06-23	104.154.70.112	2025-06-23 10:40:53.615299	\N
1556	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-17 إلى 2025-06-23	104.154.70.112	2025-06-23 10:40:56.420506	\N
1557	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-17 إلى 2025-06-23	104.154.70.112	2025-06-23 10:40:57.478318	\N
1558	export	employee_basic_report	179	\N	\N	\N	تم تصدير التقرير الأساسي المصمم للموظف: OMAR ABDULWAHAB MOHS AL MAGHREBI مع الصور	\N	2025-06-23 20:40:47.32717	\N
1559	generate_notification	salary	95	\N	\N	\N	تم إنشاء إشعار راتب للموظف: ‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI لشهر 5/2025	\N	2025-06-24 05:23:17.679174	\N
1560	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-20 إلى 2025-06-24	34.60.193.23	2025-06-24 10:37:19.168585	\N
1561	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-20 إلى 2025-06-24	34.60.193.23	2025-06-24 10:37:24.086429	\N
1562	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-20 إلى 2025-06-24	34.60.193.23	2025-06-24 10:37:25.789381	\N
1563	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-20 إلى 2025-06-24	34.60.193.23	2025-06-24 10:37:31.413055	\N
1564	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-20 إلى 2025-06-24	34.60.193.23	2025-06-24 10:37:33.737293	\N
1565	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-20 إلى 2025-06-24	34.60.193.23	2025-06-24 10:37:34.611289	\N
1566	delete	document	58	\N	\N	\N	تم حذف وثيقة من نوع national_id للموظف: EMAD AKASH GADAL ELNOUR 	\N	2025-06-24 11:47:32.943121	8
1567	update	document	16	\N	\N	\N	تم تحديث تاريخ انتهاء وثيقة national_id للموظف: ALI ELSAYED ALI ABDALLA من 2025-06-11 إلى 2025-09-11	\N	2025-06-24 11:51:49.164881	8
1568	update	document	15	\N	\N	\N	تم تحديث تاريخ انتهاء وثيقة national_id للموظف: FRID MOKHTAR AHMED ANABA من 2025-06-11 إلى 2025-09-09	\N	2025-06-24 12:03:07.975507	8
1569	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-25 إلى 2025-06-25	35.223.13.181	2025-06-25 11:52:19.590532	\N
1570	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-25 إلى 2025-06-25	35.223.13.181	2025-06-25 11:52:21.353744	\N
1571	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-25 إلى 2025-06-25	35.223.13.181	2025-06-25 11:52:22.17886	\N
1572	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-25 إلى 2025-06-25	35.223.13.181	2025-06-25 11:52:24.270338	\N
1573	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-25 إلى 2025-06-25	35.223.13.181	2025-06-25 11:52:25.237002	\N
1574	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-25 إلى 2025-06-25	35.223.13.181	2025-06-25 11:52:25.747661	\N
1575	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:22:51.162234	\N
1576	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:22:52.884079	\N
1577	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:22:53.664884	\N
1578	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:22:55.732409	\N
1579	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:22:56.702028	\N
1580	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:22:57.201761	\N
1581	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:22:57.810574	\N
1582	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:22:58.819113	\N
1583	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:22:59.412812	\N
1584	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:23:00.611814	\N
1585	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:23:01.256271	\N
1586	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-26 إلى 2025-06-26	35.232.111.100	2025-06-26 11:23:01.667134	\N
1587	export	vehicle	20	\N	\N	\N	تم تصدير بيانات السيارة 3228 ب س ن- إلى Excel	\N	2025-06-28 10:42:12.6075	\N
1588	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-22 إلى 2025-06-28	35.184.122.198	2025-06-28 10:44:00.003415	\N
1589	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-22 إلى 2025-06-28	35.184.122.198	2025-06-28 10:44:06.571065	\N
1590	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-22 إلى 2025-06-28	35.184.122.198	2025-06-28 10:44:09.000978	\N
1591	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-22 إلى 2025-06-28	35.184.122.198	2025-06-28 10:44:17.22527	\N
1592	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-22 إلى 2025-06-28	35.184.122.198	2025-06-28 10:44:20.426241	\N
1593	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-22 إلى 2025-06-28	35.184.122.198	2025-06-28 10:44:21.570202	\N
1594	update	document	21	\N	\N	\N	تم تحديث تاريخ انتهاء وثيقة national_id للموظف: SEKH AKRAM SEKH SULAIMAN من 2025-06-25 إلى 2025-09-23	\N	2025-06-28 10:58:43.363199	8
1595	update	document	27	\N	\N	\N	تم تحديث تاريخ انتهاء وثيقة national_id للموظف: IDREES KHURSHID من 2025-06-09 إلى 2025-09-07	\N	2025-06-28 11:07:49.632124	8
1596	export	vehicle	9	\N	\N	\N	تم تصدير بيانات السيارة 3186- ب س ن- إلى Excel	\N	2025-06-28 21:44:19.13103	\N
1597	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-25 إلى 2025-06-29	35.184.122.198	2025-06-29 18:37:33.621119	\N
1598	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-25 إلى 2025-06-29	35.184.122.198	2025-06-29 18:37:38.09005	\N
1599	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-25 إلى 2025-06-29	35.184.122.198	2025-06-29 18:37:39.856893	\N
1600	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-25 إلى 2025-06-29	35.184.122.198	2025-06-29 18:37:45.465154	\N
1601	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-25 إلى 2025-06-29	35.184.122.198	2025-06-29 18:37:47.706541	\N
1602	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-25 إلى 2025-06-29	35.184.122.198	2025-06-29 18:37:48.570455	\N
1603	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-25 إلى 2025-06-30	35.184.122.198	2025-06-29 18:37:50.519116	\N
1604	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-25 إلى 2025-06-30	35.184.122.198	2025-06-29 18:37:55.682801	\N
1605	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-25 إلى 2025-06-30	35.184.122.198	2025-06-29 18:37:57.858278	\N
1606	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-25 إلى 2025-06-30	35.184.122.198	2025-06-29 18:38:04.395903	\N
1607	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-25 إلى 2025-06-30	35.184.122.198	2025-06-29 18:38:06.99974	\N
1608	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-25 إلى 2025-06-30	35.184.122.198	2025-06-29 18:38:07.966222	\N
1609	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-25 إلى 2025-06-30	34.121.19.132	2025-06-29 18:38:09.728424	\N
1610	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-25 إلى 2025-06-30	34.121.19.132	2025-06-29 18:38:14.269132	\N
1611	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-25 إلى 2025-06-30	34.121.19.132	2025-06-29 18:38:15.992871	\N
1612	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-25 إلى 2025-06-30	34.121.19.132	2025-06-29 18:38:21.667522	\N
1613	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-25 إلى 2025-06-30	34.121.19.132	2025-06-29 18:38:24.016162	\N
1614	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-25 إلى 2025-06-30	34.121.19.132	2025-06-29 18:38:24.895454	\N
1615	update	document	11	\N	\N	\N	تم تحديث تاريخ انتهاء وثيقة national_id للموظف: MOHAMMED MOQBEL M. ABDULLAH GHANEM من 2025-05-30 إلى 2025-08-28	\N	2025-07-01 13:50:05.844495	8
1616	update	document	23	\N	\N	\N	تم تحديث تاريخ انتهاء وثيقة national_id للموظف: MD SIAM من 2025-06-28 إلى 2025-09-26	\N	2025-07-01 14:12:26.725745	8
1617	update	document	31	\N	\N	\N	تم تحديث تاريخ انتهاء وثيقة national_id للموظف: MD OHAB ALI  من 2025-06-30 إلى 2025-09-28	\N	2025-07-02 15:01:38.253688	8
1618	update	document	29	\N	\N	\N	تم تحديث تاريخ انتهاء وثيقة national_id للموظف: MUHAMMAD MUNEEB SULTANI GUL من 2025-03-17 إلى 2025-09-13	\N	2025-07-02 15:02:10.913727	8
1619	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-06-30 إلى 2025-07-03	34.121.19.132	2025-07-03 12:25:41.592011	\N
1620	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-06-30 إلى 2025-07-03	34.121.19.132	2025-07-03 12:25:46.905721	\N
1621	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-06-30 إلى 2025-07-03	34.121.19.132	2025-07-03 12:25:48.882575	\N
1622	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-06-30 إلى 2025-07-03	34.121.19.132	2025-07-03 12:25:55.46619	\N
1623	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-06-30 إلى 2025-07-03	34.121.19.132	2025-07-03 12:25:58.128547	\N
1624	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-06-30 إلى 2025-07-03	34.121.19.132	2025-07-03 12:25:59.104628	\N
1625	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-07-06 إلى 2025-07-06	10.81.10.202	2025-07-06 13:12:13.458941	\N
1626	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-07-06 إلى 2025-07-06	10.81.10.202	2025-07-06 13:12:15.170554	\N
1627	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-07-06 إلى 2025-07-06	10.81.10.202	2025-07-06 13:12:15.952766	\N
1628	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-07-06 إلى 2025-07-06	10.81.10.202	2025-07-06 13:12:18.034415	\N
1629	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-07-06 إلى 2025-07-06	10.81.10.202	2025-07-06 13:12:19.025281	\N
1630	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-07-06 إلى 2025-07-06	10.81.10.202	2025-07-06 13:12:19.528066	\N
1631	mass_attendance	department	7	قسم تقني	\N	\N	تم تسجيل حضور جماعي لقسم قسم تقني للفترة من 2025-07-06 إلى 2025-07-06	10.81.10.202	2025-07-06 13:12:19.891644	\N
1632	mass_attendance	department	2	Aramex Liber	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Liber للفترة من 2025-07-01 إلى 2025-07-06	10.81.3.14	2025-07-06 13:12:25.522013	\N
1633	mass_attendance	department	1	Aramex Coruer	\N	\N	تم تسجيل حضور جماعي لقسم Aramex Coruer للفترة من 2025-07-01 إلى 2025-07-06	10.81.3.14	2025-07-06 13:12:31.400021	\N
1634	mass_attendance	department	3	DHL	\N	\N	تم تسجيل حضور جماعي لقسم DHL للفترة من 2025-07-01 إلى 2025-07-06	10.81.3.14	2025-07-06 13:12:33.568417	\N
1635	mass_attendance	department	4	FLOW	\N	\N	تم تسجيل حضور جماعي لقسم FLOW للفترة من 2025-07-01 إلى 2025-07-06	10.81.3.14	2025-07-06 13:12:40.997889	\N
1636	mass_attendance	department	5	Suleiman Al Habib	\N	\N	تم تسجيل حضور جماعي لقسم Suleiman Al Habib للفترة من 2025-07-01 إلى 2025-07-06	10.81.3.14	2025-07-06 13:12:43.916638	\N
1637	mass_attendance	department	6	Project Supervisors	\N	\N	تم تسجيل حضور جماعي لقسم Project Supervisors للفترة من 2025-07-01 إلى 2025-07-06	10.81.3.14	2025-07-06 13:12:44.977676	\N
1638	mass_attendance	department	7	قسم تقني	\N	\N	تم تسجيل حضور جماعي لقسم قسم تقني للفترة من 2025-07-01 إلى 2025-07-06	10.81.3.14	2025-07-06 13:12:45.296141	\N
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public."user" (id, email, name, firebase_uid, password_hash, profile_picture, role, created_at, last_login, is_active, auth_type, employee_id, assigned_department_id, company_id, user_type, parent_user_id, created_by) FROM stdin;
12	m@m.com	محمد مقبل محمد عبدالله	\N	scrypt:32768:8:1$UpvkZjF4d6K2nXsh$72fb3be6e0fc5c7029c37821bfa4897426982aad7e5bcc9afdb1dc23b45e6c5fea7fd737b6acc01efbaa8200e0a535ed7f4add8997c93feec773e406ca5bd9e7	\N	FLEET	2025-07-06 13:18:08.053174	\N	t	local	\N	1	\N	EMPLOYEE	\N	\N
8	skrkhtan@gmail.com	Eissa Ali	\N	scrypt:32768:8:1$NuSssTB1M9PEW1UF$e7b1a30ded30568eb59d5b8310c8b6d9a64a25d8063abd25df89a800ca97a94a51050c1174dc4cf3bd45ae646e117b6b0baf84ef8f3ec8406c0566d1f59ef54f	\N	ADMIN	2025-06-20 22:45:40.326715	2025-07-08 18:25:53.153503	t	local	\N	\N	\N	EMPLOYEE	\N	\N
9	z.alhamdani@rassaudi.com	زياد محمد علي حسن	\N	scrypt:32768:8:1$Xknhs15uxdzkakU4$8a1dcb9834401e280ebb5d099676d1ae013d88a770a71152c80fe6001ac368fc5e2dc6c355bf4fbca5a6048e06debb2e101bcea28dfb6cb3311951f22f0d6cc5	\N	USER	2025-06-20 22:46:44.797191	2025-06-22 11:00:25.280095	t	local	\N	1	\N	EMPLOYEE	\N	\N
10	admin@nuzum.sa	مدير النظام	\N	scrypt:32768:8:1$1FwojbfR8N2Ypt3o$70c78d8b00444f3086a6ff3e0e34bfa0cd732afbaf79bc4cca17490543ef13520eab64f57ae4037b1180ff1df40ccd39f237da1dea682e09fb1cb5f4a56b83d3	\N	ADMIN	2025-06-20 22:57:42.916814	2025-07-01 19:36:05.068339	t	email	\N	\N	1	SYSTEM_ADMIN	\N	\N
\.


--
-- Data for Name: user_accessible_departments; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.user_accessible_departments (user_id, department_id) FROM stdin;
12	1
\.


--
-- Data for Name: user_department_access; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.user_department_access (id, user_id, department_id, created_at) FROM stdin;
21	9	1	2025-06-20 22:47:31.854168
\.


--
-- Data for Name: user_permission; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.user_permission (id, user_id, module, permissions) FROM stdin;
47	9	EMPLOYEES	31
48	9	ATTENDANCE	31
49	9	VEHICLES	31
53	12	VEHICLES	31
\.


--
-- Data for Name: vehicle; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle (id, plate_number, make, model, year, color, status, notes, created_at, updated_at, authorization_expiry_date, registration_expiry_date, inspection_expiry_date, driver_name, company_id) FROM stdin;
17	3218- ب س ن	نيسان	ارفان	2021	ابيض	available		2025-04-23 15:32:21.426084	2025-07-06 14:45:37.62594	2025-09-19	\N	2023-01-01	OMAR ABDULWAHAB MOHS AL MAGHREBI	1
10	3189-ب س ن	نيسان	ارفان	2021	برند ارامكس	in_workshop	حادث نسبة الخطاء على دامل 	2025-04-23 15:29:28.398178	2025-07-03 09:32:00.386045	2025-08-11	\N	2023-01-01	MOHAMMED DAMAL FAQIR HUSSAIN	1
5	3220 ب س ن 	نيسان	اورفن	2021	برند -ارامكس	in_workshop	حادث على صالح ناصر	2025-04-23 15:20:39.015095	2025-07-03 09:32:25.65934	2025-07-22	\N	2023-01-01	‏SALEH NASSER YASLAM BAANS	1
8	3176- ب س ن 	نيسان	ارفان	2021	برند ارامكس	in_workshop	حادث طاهر نسبة الخطاء على الطرف الثاني 	2025-04-23 15:28:49.524853	2025-07-03 09:43:30.446796	\N	\N	2026-02-02	TAHIR ALI MEHBOOB ALI	1
14	3206- ب س ن	نيسان	ارفان	2021	برند ارامكس	available		2025-04-23 15:31:06.916185	2025-07-06 10:47:59.902742	2025-06-06	\N	\N	ABBAS AMEEN QAID QASEM	1
21	7277 - ا س ل	بادجت	نيسان اورفان	2023	ابيض	available	بديله عن السيارة 3943 اس ص  حادث السيارة مؤقت	2025-05-28 08:37:17.347097	2025-07-03 09:44:15.203988	2025-09-23	\N	2025-11-17	‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI	1
23	ABC-123	تويوتا	كامري	2022	أبيض	active	\N	2025-07-06 10:05:59.704199	2025-07-07 22:58:43.700546	\N	\N	\N	ABBAS AMEEN QAID QASEM	1
19	3133- ب ط ط	تايوتا	هايس	2023	ابيض	in_workshop		2025-04-23 16:27:45.025638	2025-07-05 18:11:55.220122	2025-06-14	\N	2026-01-27	MOHAMMED MOQBEL M. ABDULLAH GHANEM	1
24	XYZ-456	هيونداي	إلنترا	2021	أسود	active	\N	2025-07-06 10:05:59.704199	2025-07-08 20:33:25.634745	\N	\N	\N	ABBAS AMEEN QAID QASEM	1
3	1903 - اس ا	نيسان	اورفان	2022	ابيض	in_project		2025-04-23 15:18:13.447227	2025-05-29 12:01:15.086681	2025-09-02	\N	2025-10-19	HUSSAM AL DAIN	1
4	3215- ب س ن	نيسان	اورفان	2021	برند ارامكس	in_project		2025-04-23 15:18:54.633973	2025-05-29 13:06:51.914202	\N	\N	2025-02-01	SHABEER MULLA PALLI	1
6	3230 - ب س ن	نيسان	اورفان	2021	ابيض	in_project		2025-04-23 15:26:55.425089	2025-05-29 13:13:53.860396	2025-07-08	\N	2026-02-26	‏HASAN MOHAMMED ALI RAGEH‏	1
13	3709-ب ط ق	نيسان	ارفان	2021	ابيض	in_project		2025-04-23 15:30:41.710219	2025-05-29 13:16:07.334968	\N	\N	2026-03-13	MOHAMMED MOQBEL M. ABDULLAH GHANEM	1
2	3131-TTB	تايوتا	هايس	2023	ابيض	in_project		2025-04-20 19:45:36.583061	2025-05-29 10:47:32.905933	2025-09-23	\N	2026-02-23	WADHAH NABIL QASEM QAID AL TAHERI 	1
11	3203- ب س ن	نيسان	ارفان	2021	برند ارامكس	in_project		2025-04-23 15:29:54.351234	2025-05-29 13:07:57.405041	2025-07-11	\N	2023-01-01	MOHAMED MUBARK YOUSIF ELAMIN	1
18	3943-  ا س ا	نيسان	ارفان	2021	ابيض	in_project	حادث على محمود محمد ناجي  تبقا 1000 على محمود \r\nالسيارة تم نقلة الا الدمام  امزن الاحساء  ----- اسم السائق ---- بشير عبد الرحمان حميدو 	2025-04-23 15:33:14.23317	2025-07-05 12:35:36.063172	\N	\N	\N	بشير عبد الرحمن حملا   يدو--امازون الاحساء 	1
9	3186- ب س ن	نيسان	ارفان	2021	ابيض	in_project	تم نقل السيارة من القصيم الا امازون الاحساء -- حيث تم سحب السيارة---- من -- عباس امين --3907 ---بعد سحب السيارة من حمد مقبل \r\n	2025-04-23 15:29:09.438103	2025-07-05 13:30:41.782977	\N	\N	\N	محمد بشرى محمد علي -- امزون الاحساء 	1
15	3185-ب س ن	نيسان	ارفان	2021	ابيض	in_workshop	دينمو	2025-04-23 15:31:27.246168	2025-07-03 09:31:32.458639	2025-09-23	\N	2023-01-01	SAIF UL REHMAN  MUHAMMAD IRSHADA	1
22	3229 ب س ن	نيسان	ارفان	2021	برند ارامكس	in_workshop	حراره في المحرك	2025-06-24 10:50:48.181015	2025-07-03 09:32:47.583211	\N	\N	\N		\N
25	DEF-789	نيسان	سنترا	2023	فضي	active	\N	2025-07-06 10:05:59.704199	2025-07-06 10:05:59.704199	\N	\N	\N	\N	1
20	3228 ب س ن	نيسان اورفان	2021	2021	ابيض	in_project		2025-05-14 20:53:16.895135	2025-07-06 10:32:38.610238	2025-09-16	\N	\N	ABBAS AMEEN QAID QASEM	1
12	1493- ب س ق	نيسان	ارفان	2021	برند ارامكس	in_project		2025-04-23 15:30:15.606251	2025-07-06 11:04:26.436212	2025-06-17	\N	2023-01-01	ABBAS AMEEN QAID QASEM	1
7	3204 - ب س ن	نيسان	اورفان	2021	برند ارامكس	in_workshop	السيارة في الورشة --- حرارة 	2025-04-23 15:28:03.957184	2025-07-06 12:26:04.350227	2025-07-23	\N	2023-01-01	‏MOHMOOD MOHAMMED HAMOOD NAJI AL GHMAI	1
\.


--
-- Data for Name: vehicle_accident; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_accident (id, vehicle_id, accident_date, driver_name, accident_status, vehicle_condition, deduction_amount, deduction_status, accident_file_link, location, description, police_report, insurance_claim, notes, created_at, updated_at, liability_percentage) FROM stdin;
4	18	2025-03-27	محمود محمد ناجي جحمل	قيد المعالجة	يوجد تلفيات	2000	t	https://drive.google.com/file/d/1qVDUA4d0Fm8rBcCpHilAnffGwmJA656P/view?usp=drive_link	حائل		t	f		2025-05-28 09:30:08.419663	2025-05-28 09:30:08.419665	100
5	5	2025-07-02	صالح ناصر باعانس 	قيد المعالجة	في الورشة 	2000	f	https://drive.google.com/file/d/1wUTJh0ef3IcbKj9dabmnkbEQxqzuNL97/view?usp=drive_link	القصيم - بريدة		t	f		2025-07-02 14:34:14.93672	2025-07-02 14:34:54.19284	100
6	10	2025-07-02	محمد دامل فقسر حسين 	قيد المعالجة	في الورشة 	2000	f	https://drive.google.com/file/d/1mvmBAS0tevS7PTj-ARS7V3-TT8vaGHAW/view?usp=drive_link		قام الموظف بتسبب بي تلفيات اسفل المركبة شملة الذارعة والميازين  وبعد تقدير الاضرار تبين انا تكلفة الاصلاحات تبلف8400   تم سحب السيارة من الورشة وعمل حادث بي السيارة وتم تقيد الحادث بي اسم المندوب وتم تسليم السيارة والتقرير الا امان السريع	f	f		2025-07-02 14:40:48.408561	2025-07-02 14:40:48.408564	100
3	8	2025-05-22	طاهر محبوب 	قيد المعالجة		0	f	https://drive.google.com/file/d/11ry0qxSHwZU8Ehi1XL2mbhS1azXLWjYx/view?usp=drive_link	بريدة الصفراء القصيم 	هذا التقرير النهائي لتحديد المسؤولية يتعلق بحادث وقع في 2 مايو 2025 الساعة 11:20:52 صباحًا في طريق الملك فيصل، حي الصفاء، بريدة.\r\n\r\nملخص معلومات الحادث:\r\nعدد أطراف الحادث: 2\r\nعدد الإصابات: 10\r\nعدد الوفيات: 0\r\nسبب الحادث: عدم ترك مسافة كافية.\r\nالأنظمة المخالفة: نظام المرور المادة رقم 50/2/19.\r\nالطرف الأول (يوسف محمد محمد اسماعيل):\r\nالجنسية: مصري\r\nالعمر: 62 سنة\r\nنوع الرخصة: خاصة، وتنتهي في 5 يوليو 1448 هـ.\r\nالمركبة: مرسيدس / E240، موديل 2004، لون أسود، رقم اللوحة ب س ص 3709 / خصوصي.\r\nشركة التأمين: شركة الاتحاد للتأمين التعاوني، نوع التأمين شامل، وينتهي في 28 ديسمبر 2025.\r\nنسبة المسؤولية: 100%\r\nجهة الصدمة: المقدمة، الركن الأمامي الأيمن، الجانب الأيمن، وأضرار داخلية، الكفر الأمامي الأيمن.\r\nالطرف الثاني (طاهر على محبوب على):\r\nالجنسية: باكستاني\r\nالعمر: 24 سنة\r\nنوع الرخصة: خاصة، وتنتهي في 21 أبريل 1451 هـ.\r\nالمركبة: نيسان / فان بضاعة، موديل 2021، لون أبيض، رقم اللوحة ب س ن 3176 / نقل خاص.\r\nشركة التأمين: شركة الدرع العربي للتأمين التعاوني، نوع التأمين مسؤولية ضد الغير - مركبة، وينتهي في 19 يونيو 2025.\r\nنسبة المسؤولية: 0%\r\nجهة الصدمة: المؤخرة، الركن الخلفي الأيسر، الجانب الأيسر، أضرار داخلية، الكفر الخلفي الأيسر.\r\nوصف الحادث:\r\n\r\nبعد المعاينة والاستماع لأقوال الطرفين، تبين أن الطرفين كانا يسيران على نفس المسار في شارع الملك فيصل باتجاه الشرق. بسبب عدم ترك مسافة كافية من قبل الطرف الأول، حدث تصادم أدى إلى تلفيات في مركبتي الطرفين.	t	f		2025-05-22 07:50:52.690716	2025-07-02 15:52:25.194216	0
\.


--
-- Data for Name: vehicle_checklist; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_checklist (id, vehicle_id, inspection_date, inspector_name, inspection_type, status, notes, created_at, updated_at) FROM stdin;
2	3	2025-05-15	Hhggt	monthly	completed		2025-05-15 13:56:10.018676	2025-05-15 13:56:10.018679
3	3	2025-05-15	متكمكمتكت	daily	completed		2025-05-15 14:06:16.0117	2025-05-15 14:06:16.011703
4	3	2025-05-15	تك	weekly	completed		2025-05-15 16:30:31.862863	2025-05-15 16:30:31.862866
\.


--
-- Data for Name: vehicle_checklist_image; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_checklist_image (id, checklist_id, image_path, image_type, description, created_at) FROM stdin;
1	4	uploads/vehicles/checklists/20250515163031_2cf21454c0d54c458749173c4c121d0e_logo.png	inspection		2025-05-15 16:30:31.947226
2	4	uploads/vehicles/checklists/20250515163031_19eea282f83a488d8241503a2bffcb95_logo1.jpg	inspection		2025-05-15 16:30:31.947229
3	4	uploads/vehicles/checklists/20250515163031_a8fffa286809431e9b7d54ceda031b1b_Rassaudi.jpg	inspection		2025-05-15 16:30:31.947229
4	4	uploads/vehicles/checklists/20250515163031_489e99bb314341118bafa93254836f74_Screenshot_2025-03-19_011159.png	inspection		2025-05-15 16:30:31.94723
5	4	uploads/vehicles/checklists/20250515163031_e8a9d4aa3122436a8fe61dabd7e26db9_Screenshot_2025-04-22_223357-removebg-preview.png	inspection		2025-05-15 16:30:31.94723
6	4	uploads/vehicles/checklists/20250515163031_43a2c924716248978afdf91cb39b884f_shrk-rasko-alsaaody-almhdod-1644097395-915.png	inspection		2025-05-15 16:30:31.94723
7	4	uploads/vehicles/checklists/20250515163031_f407e03164f347d38abfd5e336294f61_WhatsApp_Image_2025-05-11_at_18.12.14_866fda64.jpg	inspection		2025-05-15 16:30:31.947231
8	4	uploads/vehicles/checklists/20250515163031_3b00af4fe85a47829346d88d42fb00b7_WhatsApp_Image_2025-05-11_at_21.23.50_2331cebf.jpg	inspection		2025-05-15 16:30:31.947231
\.


--
-- Data for Name: vehicle_checklist_item; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_checklist_item (id, checklist_id, category, item_name, status, notes, created_at, updated_at) FROM stdin;
28	2	المحرك والسوائل	زيت المحرك	good		2025-05-15 13:56:10.083588	2025-05-15 13:56:10.083592
29	2	المحرك والسوائل	سائل الفرامل	good		2025-05-15 13:56:10.083619	2025-05-15 13:56:10.08362
30	2	المحرك والسوائل	سائل التبريد	good		2025-05-15 13:56:10.083621	2025-05-15 13:56:10.083622
31	2	المحرك والسوائل	سائل باور الدركسون	good		2025-05-15 13:56:10.083623	2025-05-15 13:56:10.083623
32	3	المحرك والسوائل	سائل الفرامل	poor		2025-05-15 14:06:16.082314	2025-05-15 14:06:16.082318
33	3	المحرك والسوائل	سائل التبريد	poor		2025-05-15 14:06:16.082321	2025-05-15 14:06:16.082322
34	4	المحرك	مستوى زيت المحرك	good		2025-05-15 16:30:32.005769	2025-05-15 16:30:32.005772
35	4	المحرك	مستوى سائل التبريد	good		2025-05-15 16:30:32.005773	2025-05-15 16:30:32.005773
36	4	الإطارات	ضغط الإطارات	good		2025-05-15 16:30:32.005774	2025-05-15 16:30:32.005774
37	4	الإطارات	حالة الإطارات	good		2025-05-15 16:30:32.005774	2025-05-15 16:30:32.005775
38	4	الإضاءة	المصابيح الأمامية	good		2025-05-15 16:30:32.005775	2025-05-15 16:30:32.005775
39	4	الإضاءة	المصابيح الخلفية	good		2025-05-15 16:30:32.005775	2025-05-15 16:30:32.005776
\.


--
-- Data for Name: vehicle_damage_marker; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_damage_marker (id, checklist_id, marker_type, position_x, position_y, color, size, notes, created_at) FROM stdin;
\.


--
-- Data for Name: vehicle_fuel_consumption; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_fuel_consumption (id, vehicle_id, date, liters, cost, kilometer_reading, driver_name, fuel_type, filling_station, notes, created_at) FROM stdin;
\.


--
-- Data for Name: vehicle_handover; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_handover (id, handover_type, handover_date, mileage, handover_time, project_name, city, vehicle_id, employee_id, supervisor_employee_id, vehicle_car_type, vehicle_plate_number, vehicle_model_year, person_name, driver_company_id, driver_phone_number, driver_residency_number, driver_contract_status, driver_license_status, driver_signature_path, supervisor_name, supervisor_company_id, supervisor_phone_number, supervisor_residency_number, supervisor_contract_status, supervisor_license_status, supervisor_signature_path, reason_for_change, vehicle_status_summary, notes, reason_for_authorization, authorization_details, fuel_level, has_spare_tire, has_fire_extinguisher, has_first_aid_kit, has_warning_triangle, has_tools, has_oil_leaks, has_gear_issue, has_clutch_issue, has_engine_issue, has_windows_issue, has_tires_issue, has_body_issue, has_electricity_issue, has_lights_issue, has_ac_issue, movement_officer_name, movement_officer_signature_path, damage_diagram_path, form_link, custom_company_name, custom_logo_path, created_at) FROM stdin;
3	تسليم	2025-01-05	45200	\N	مشروع جدة	جدة	23	178	\N	\N	3219-ب س ن	2020	محمد أحمد السالم	\N	0509876543	\N	\N	\N	\N	خالد عبدالله المشرف	\N	\N	\N	\N	\N	\N	\N	حالة ممتازة	تسليم للموظف الجديد	\N	\N	ممتلئ	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f	\N	\N	\N	\N	\N	\N	2025-07-06 10:20:07.057788
4	تسليم	2024-11-20	38000	\N	مشروع الدمام	الدمام	10	178	\N	\N	3189-ب س ن	2021	محمد أحمد السالم	\N	0509876543	\N	\N	\N	\N	سعد محمد المشرف	\N	\N	\N	\N	\N	\N	\N	حالة ممتازة	تسليم مركبة جديدة	\N	\N	ممتلئ	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f	\N	\N	\N	\N	\N	\N	2025-07-06 10:20:07.057788
5	تسليم	2024-10-15	42000	\N	مشروع مكة	مكة	5	180	\N	\N	3220 ب س ن	2019	خالد عبدالله النصر	\N	0507654321	\N	\N	\N	\N	فهد علي المشرف	\N	\N	\N	\N	\N	\N	\N	حالة جيدة	تسليم للموظف الجديد	\N	\N	ثلاثة أرباع	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f	\N	\N	\N	\N	\N	\N	2025-07-06 10:20:07.057788
6	استلام	2024-11-30	39500	\N	مشروع الطائف	الطائف	14	182	\N	\N	3206- ب س ن	2018	سعد محمد الراشد	\N	0503216540	\N	\N	\N	\N	ماجد سالم المشرف	\N	\N	\N	\N	\N	\N	\N	حالة مقبولة	إرجاع بعد انتهاء العقد	\N	\N	ربع ممتلئ	t	f	t	t	t	f	f	f	f	f	f	f	f	f	f	\N	\N	\N	\N	\N	\N	2025-07-06 10:20:07.057788
7	delivery	2025-07-06	12345	13:29:00	ارامكس 	القصيم - بريدة	20	174	223	نيسان اورفان 2021	3228 ب س ن	2021	ABBAS AMEEN QAID QASEM	50685.0	545593215	2370503332.0	\N	\N	signatures/2b55045afe43401bb6e51f9208d20811.png	ZEYAD MOHAMMAD ALI HASAN	3288	0593214413	3288	\N	\N	signatures/5b502cc856c34cf38f84e005fdca7648.png	لا يوجد	نلتلنتلنتلنتلنتلنلت		\N	\N	3/4	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	diagrams/bdf2c9c20e844895819f9539bd93b7d6.png		\N	\N	2025-07-06 10:32:38.209849
10	return	2025-07-06	12345	16:58:00	ارامكس 	القصيم - بريدة	17	175	223	نيسان ارفان	3218- ب س ن	2021	MOHAMMED MOQBEL M. ABDULLAH GHANEM	8621.0	543949234	2502086529	Active	Valid	signatures/21ee43e36a634dfb9196f85b00aec3e2.png	ZEYAD MOHAMMAD ALI HASAN	3288	0593214413	3288	\N	\N	signatures/f389f09f08b14f69874f1c895501025a.png		نلتلنتلنتلنتلنتلنلت		\N	\N	full	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	diagrams/669aee88bed845b0b7167d99fa58f3f8.png	https://acrobat.adobe.com/id/urn:aaid:sc:AP:ec63657b-e895-42cd-812f-3c5c5ecbd812	\N	\N	2025-07-06 14:00:15.613315
12	delivery	2025-07-06	156546	17:41:00	ارامكس	القصيم	17	179	223	نيسان ارفان	3218- ب س ن	2021	OMAR ABDULWAHAB MOHS AL MAGHREBI	4298	593214434	2489682019	Active	Valid	signatures/29ab717a620148d9aa7f65b44f47fa2c.png	ZEYAD MOHAMMAD ALI HASAN	3288	0593214413	3288	\N	\N	signatures/5c3402dffed342bba33788cf4d5cf5d9.png	اساسيه	يوجد ملاحظات	‏هذا الراكب خربان لا ينزل إرتخاء في دعست الراكب جهيمان خدش في الصدام الخلفي ضربة تحت باب السحاب سر تقطيع في المراتب الداخلية كورس السواق كسر في اللوحة الأمامية شعار Nissan غير موجود على الصدام الأمامي اتخاف في الصدام الأمامي تحت الكشاف يسار\r\n‏ضربة تحت باب السحاب يمين	\N	\N	full	f	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	diagrams/1d01d12cc54c41239976360cb8e1dc80.png	https://drive.google.com/file/d/1Med4eLL7Kf5RhxmX7FqNic1M_qtkERQ_/view?usp=drive_link	\N	\N	2025-07-06 14:45:39.24852
13	return	2025-07-06	12345	17:53:00	ارامكس 	القصيم - بريدة	17	175	175	نيسان ارفان	3218- ب س ن	2021	MOHAMMED MOQBEL M. ABDULLAH GHANEM	8621.0	543949234	2502086529	Active	Valid	signatures/03b1924564274577bdb7708fa2447b24.png	MOHAMMED MOQBEL M. ABDULLAH GHANEM	8621.0	543949234	2502086529	Active	Valid	signatures/d835f7d11d284dacbea30b63346849e2.png	kkjkj	نلتلنتلنتلنتلنتلنلت		\N	\N	1/2	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	diagrams/259f8520764047e6877e9b1a0c03512d.png		\N	\N	2025-07-06 15:03:24.745986
14	inspection	2025-07-06	64646464	18:08:00	Jzjsjs	Jsjsjsjs	17	174	174	نيسان ارفان	3218- ب س ن	2021	ABBAS AMEEN QAID QASEM	50685.0	545593215	2370503332.0	\N	\N	signatures/c4a7cac04f0346f3aa9aaed510e06783.png	ABBAS AMEEN QAID QASEM	50685.0	545593215	2370503332.0	\N	\N	signatures/057a8c78b1d64dd98fdabd80d84df24b.png	Hsjsjsjs		Ididjdj	\N	\N	ممتلئ	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	diagrams/9e4e23a971844676b87704e0492e2f1f.png		\N	\N	2025-07-06 15:09:06.378108
24	return	2025-07-06	12345678	23:08:00	ارامكس 	القصيم - بريدة	23	224	193	تويوتا كامري	ABC-123	2022	EISSA ALI  ABDOULLH MOHAMMED	8352	0558619232	2290833975	\N	\N	signatures/4db1bf228c464c3aa5a9130270228f2b.png	ALI ELSAYED ALI ABDALLA	8804	0550407908	2516571086	\N	\N	signatures/994eefbc48a0461ab33ab9c82c5e3557.png	kjlkj			\N	\N	ممتلئ	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	\N	https://drive.google.com/drive/folders/1FVK3R8D_Dom7gQyaHJMgkbgvqVyeaB_V	\N	\N	2025-07-06 20:15:05.929496
25	delivery	2025-07-07	123456	01:57:00	ارامكس 	القصيم - بريدة	23	174	174	تويوتا كامري	ABC-123	2022	ABBAS AMEEN QAID QASEM	50685.0	545593215	2370503332.0	\N	\N	signatures/e62ed0ba1d7b4734ab04154b22e24a5c.png	ABBAS AMEEN QAID QASEM	50685.0	545593215	2370503332.0	\N	\N	signatures/47bfd9bbb66140a981118987d66fc16d.png	بلا			\N	\N	ممتلئ	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	diagrams/56f9136853ca4b2cbe033690a4d3a9d7.png	https://d72f2aef-918c-4148-9723-15870f8c7cf6-00-2c1ygyxvqoldk.riker.replit.dev/mobile/vehicles/handover/create/3	\N	\N	2025-07-07 22:58:43.329352
26	delivery	2025-07-07	12466	02:54:00	ارامكس	القصيم	23	193	174	تويوتا كامري	ABC-123	2022	ALI ELSAYED ALI ABDALLA	8804	0550407908	2516571086	\N	\N	signatures/bb89177aa57a44fd8160ab9c61fdfdd9.png	ABBAS AMEEN QAID QASEM	50685.0	545593215	2370503332.0	\N	\N	signatures/2d28b8fbc71a4e44b38d711fd458b4b6.png	Jhhh			\N	\N	ممتلئ	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	diagrams/c4b6ff12a1a145f4aa6a63d8fcba7092.png		\N	\N	2025-07-07 23:56:22.460515
27	delivery	2025-07-08	12345	23:31:00	ارامكس	القصيم	24	174	174	هيونداي إلنترا	XYZ-456	2021	ABBAS AMEEN QAID QASEM	50685.0	545593215	2370503332.0	\N	\N	signatures/4c7eff81b72049f8ac0fdca8744997b6.png	ABBAS AMEEN QAID QASEM	50685.0	545593215	2370503332.0	\N	\N	signatures/a600bbcebd154690b309b839391dd19d.png	اساسيه	يوجد ملاحضات		\N	\N	1/2	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	diagrams/50ac7e3b8abd46359fca1bd0a1783074.png		\N	\N	2025-07-08 20:33:25.229515
8	delivery	2025-07-06	12345	13:46:00	ارامكس 	القصيم - بريدة	14	174	174	نيسان ارفان	3206- ب س ن	2021	MUHAMMAD USMAN MUHAMMAD MAQBOOL	50685.0	545593215	2370503332.0	\N	\N	signatures/c69691b14add4a9c86259eb0cfe85d8e.png	ABBAS AMEEN QAID QASEM	50685.0	545593215	2370503332.0	\N	\N	signatures/08e9a58b999f4d45977bd07f448af8d3.png	نالنلنت	نلتلنتلنتلنتلنتلنلت	يوجد ضربه جوار باب الديزل خفيف الصدام مركب مسمار يوجد ضربة  تحت باب السحاب يسارئئئ	\N	\N	full	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		signatures/ba4b33c8a1e1470e838fc3d277324777.png	diagrams/1b4f3c5bf7204f2dbcc3d91913adb832.png	https://acrobat.adobe.com/id/urn:aaid:sc:AP:0ddccade-fe3f-4b0d-bbac-9bde7ddc6af5	\N	\N	2025-07-06 10:47:59.493046
9	delivery	2025-07-06	123456	14:02:00	ارامكس 	القصيم - بريدة	12	174	223	نيسان ارفان	1493- ب س ق	2021	TAHIR ALI MEHBOOB ALI	50685.0	545593215	2370503332.0	\N	\N	signatures/e7bc578f1e79400db913c2240f31369f.png	ZEYAD MOHAMMAD ALI HASAN	3288	0593214413	3288	\N	\N	signatures/2dfb8ecbce684dce84e8ed58289e40b4.png	34567890-	LHLKHLKHLH	KHLKHLKHLHL	\N	\N	full	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	diagrams/69f7d90e1d6549af80c07da782aa1592.png	https://acrobat.adobe.com/id/urn:aaid:sc:AP:324d62c6-df0c-435e-aaf0-0aef620e44c6	\N	\N	2025-07-06 11:04:26.051044
28	return	2025-07-08	12345678	00:00:00	ارامكس 	القصيم - بريدة	23	223	174	تويوتا كامري	ABC-123	2022	ZEYAD MOHAMMAD ALI HASAN	3288	0593214413	3288			signatures/54830084082048a3baffbbb0d7ba14cf.png	ABBAS AMEEN QAID QASEM	50685.0	545593215	2370503332.0	\N	\N	signatures/f2593bfa596844388e016789ae2dba0b.png	asdfghjkl;'		aaasdfghjkl	\N	\N	ممتلئ	t	t	t	t	t	f	f	f	f	f	f	f	f	f	f		\N	diagrams/60c431c9f54847b286095611629aab82.png	https://acrobat.adobe.com/id/urn:aaid:sc:AP:7e12e9f5-b35c-4085-b89c-6ae5d975f5c1	\N	\N	2025-07-08 21:03:16.23625
\.


--
-- Data for Name: vehicle_handover_image; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_handover_image (id, handover_record_id, image_path, image_description, uploaded_at, file_path, file_type, file_description) FROM stdin;
5	92	uploads/handover/f15bf41d-dce1-4da2-a29c-38038ffe6d0c_2025-07-04_19-35.pdf		2025-07-05 11:21:31.395825	uploads/handover/f15bf41d-dce1-4da2-a29c-38038ffe6d0c_2025-07-04_19-35.pdf	pdf	
6	93	uploads/handover/bcf0c342-d45b-4aa5-9b90-65716ab22ba7_-_-_3218__2025-07-04_19-35.pdf		2025-07-05 11:34:43.70653	uploads/handover/bcf0c342-d45b-4aa5-9b90-65716ab22ba7_-_-_3218__2025-07-04_19-35.pdf	pdf	
7	94	uploads/handover/296b219f-7214-4f10-9720-4142a4934534_2025-07-04_18-06.pdf		2025-07-05 11:50:57.70212	uploads/handover/296b219f-7214-4f10-9720-4142a4934534_2025-07-04_18-06.pdf	pdf	
8	95	uploads/handover/d12f0639-9356-42da-b937-4e79e9a5db9d_3943_-07-04_18-25.pdf		2025-07-05 12:34:53.396166	uploads/handover/d12f0639-9356-42da-b937-4e79e9a5db9d_3943_-07-04_18-25.pdf	pdf	
9	96	uploads/handover/54ca251c-90b5-4d03-a6b0-1f7448b4c29c_2025-07-04_18-25.pdf		2025-07-05 12:35:36.337246	uploads/handover/54ca251c-90b5-4d03-a6b0-1f7448b4c29c_2025-07-04_18-25.pdf	pdf	
10	97	uploads/handover/579a2b7f-ce7f-4252-8e4c-9897bfba88c5_3186_--__2025-07-04_18-19.pdf		2025-07-05 13:29:26.670855	uploads/handover/579a2b7f-ce7f-4252-8e4c-9897bfba88c5_3186_--__2025-07-04_18-19.pdf	pdf	
11	98	uploads/handover/71e3e844-7d11-49d1-bfe0-b1d7dd5dc6db_2025-07-04_18-19.pdf		2025-07-05 13:30:42.051684	uploads/handover/71e3e844-7d11-49d1-bfe0-b1d7dd5dc6db_2025-07-04_18-19.pdf	pdf	
12	99	uploads/handover/7b86e505-6130-4bdc-b2d6-07a92d00f23d_3133_2025-07-05_17-34.pdf		2025-07-05 18:10:17.692498	uploads/handover/7b86e505-6130-4bdc-b2d6-07a92d00f23d_3133_2025-07-05_17-34.pdf	pdf	
13	7	uploads/handover/3ff9ed38-4175-458a-96bd-3c3a2d44946a_handover_form_3228_.pdf	نمنامنامنا	2025-07-06 10:32:38.878999	uploads/handover/3ff9ed38-4175-458a-96bd-3c3a2d44946a_handover_form_3228_.pdf	pdf	نمنامنامنا
14	9	uploads/handover/d1b0923b-a517-44a5-bebb-b394456226e0_WhatsApp_Image_2025-07-06_at_12.09.22_a5e9e4ab.jpg	HLJHLH	2025-07-06 11:04:26.711168	uploads/handover/d1b0923b-a517-44a5-bebb-b394456226e0_WhatsApp_Image_2025-07-06_at_12.09.22_a5e9e4ab.jpg	image	HLJHLH
15	9	uploads/handover/1283c26d-ccce-474c-91dc-c16572e1e79c_WhatsApp_Image_2025-07-06_at_12.06.12_c71abcb8.jpg	KJ;KJKJ	2025-07-06 11:04:26.711172	uploads/handover/1283c26d-ccce-474c-91dc-c16572e1e79c_WhatsApp_Image_2025-07-06_at_12.06.12_c71abcb8.jpg	image	KJ;KJKJ
16	10	uploads/handover/3ca8caf3-f800-4e00-be4a-1fd034751e6d_handover_form_3185-_.pdf		2025-07-06 14:00:16.249812	uploads/handover/3ca8caf3-f800-4e00-be4a-1fd034751e6d_handover_form_3185-_.pdf	pdf	
17	10	uploads/handover/45504019-3964-4ff8-8e2b-1f42bc996b55_handover_form_1493-_.pdf		2025-07-06 14:00:16.249817	uploads/handover/45504019-3964-4ff8-8e2b-1f42bc996b55_handover_form_1493-_.pdf	pdf	
18	10	uploads/handover/330b5333-ba54-4e6e-989e-ce5c5369c95a_handover_form_3186-_.pdf		2025-07-06 14:00:16.249818	uploads/handover/330b5333-ba54-4e6e-989e-ce5c5369c95a_handover_form_3186-_.pdf	pdf	
19	13	uploads/handover/48eb3039-8b21-4df4-8010-f1cc390a40c1_WhatsApp_Image_2025-07-06_at_12.09.22_a5e9e4ab.jpg		2025-07-06 15:03:25.316786	uploads/handover/48eb3039-8b21-4df4-8010-f1cc390a40c1_WhatsApp_Image_2025-07-06_at_12.09.22_a5e9e4ab.jpg	image	
20	14	uploads/handover/a431aa49-1c40-475c-9e95-9e91d75045c3_IMG-20250706-WA0233.jpg		2025-07-06 15:09:07.000464	uploads/handover/a431aa49-1c40-475c-9e95-9e91d75045c3_IMG-20250706-WA0233.jpg	image	
21	14	uploads/handover/2835eb0d-f74d-4d66-9ab9-08bb7e3140e6_IMG-20250706-WA0241.jpg		2025-07-06 15:09:07.000468	uploads/handover/2835eb0d-f74d-4d66-9ab9-08bb7e3140e6_IMG-20250706-WA0241.jpg	image	
22	14	uploads/handover/aa59c4a2-a1c9-4ec2-86e4-6303e46abcbe_IMG-20250706-WA0239.jpg		2025-07-06 15:09:07.000469	uploads/handover/aa59c4a2-a1c9-4ec2-86e4-6303e46abcbe_IMG-20250706-WA0239.jpg	image	
23	14	uploads/handover/31566bc6-cfba-408c-bbbe-55de761eb57d_IMG-20250706-WA0240.jpg		2025-07-06 15:09:07.000469	uploads/handover/31566bc6-cfba-408c-bbbe-55de761eb57d_IMG-20250706-WA0240.jpg	image	
24	14	uploads/handover/6ee2a52b-fb86-4b5c-af2c-54b61ae7e209_IMG-20250706-WA0238.jpg		2025-07-06 15:09:07.00047	uploads/handover/6ee2a52b-fb86-4b5c-af2c-54b61ae7e209_IMG-20250706-WA0238.jpg	image	
25	14	uploads/handover/4211226e-c918-4518-9023-85a18731a168_IMG-20250706-WA0237.jpg		2025-07-06 15:09:07.000471	uploads/handover/4211226e-c918-4518-9023-85a18731a168_IMG-20250706-WA0237.jpg	image	
26	14	uploads/handover/edc43ace-13bd-44fd-bc35-1b1df12ee0d9_IMG-20250706-WA0236.jpg		2025-07-06 15:09:07.000471	uploads/handover/edc43ace-13bd-44fd-bc35-1b1df12ee0d9_IMG-20250706-WA0236.jpg	image	
27	14	uploads/handover/0f68cab3-6ef3-40a3-b48b-2029c0e7a566_IMG-20250706-WA0235.jpg		2025-07-06 15:09:07.000472	uploads/handover/0f68cab3-6ef3-40a3-b48b-2029c0e7a566_IMG-20250706-WA0235.jpg	image	
150	24	uploads/handover/83e7b714-686a-46dc-931f-31acf0fd3f87_WhatsApp_Image_2025-07-06_at_18.57.10_8dea943a.jpg		2025-07-06 20:15:06.494972	uploads/handover/83e7b714-686a-46dc-931f-31acf0fd3f87_WhatsApp_Image_2025-07-06_at_18.57.10_8dea943a.jpg	image	
151	24	uploads/handover/f6aca84d-c101-42de-bec5-f4ba637128b0_WhatsApp_Image_2025-07-06_at_18.57.19_984ad30f.jpg		2025-07-06 20:15:06.494976	uploads/handover/f6aca84d-c101-42de-bec5-f4ba637128b0_WhatsApp_Image_2025-07-06_at_18.57.19_984ad30f.jpg	image	
152	24	uploads/handover/a3221746-7bfa-451b-8afc-487e2b46dfdc_WhatsApp_Image_2025-07-06_at_18.57.35_21285158.jpg		2025-07-06 20:15:06.494979	uploads/handover/a3221746-7bfa-451b-8afc-487e2b46dfdc_WhatsApp_Image_2025-07-06_at_18.57.35_21285158.jpg	image	
153	24	uploads/handover/ef06f824-d109-4344-8ced-5be03fb54440_WhatsApp_Image_2025-07-06_at_18.57.35_a014f68a.jpg		2025-07-06 20:15:06.49498	uploads/handover/ef06f824-d109-4344-8ced-5be03fb54440_WhatsApp_Image_2025-07-06_at_18.57.35_a014f68a.jpg	image	
154	24	uploads/handover/d3e68d14-0422-4eb6-bee2-cf410625d7c0_WhatsApp_Image_2025-07-06_at_18.57.53_ddd9124c.jpg		2025-07-06 20:15:06.494981	uploads/handover/d3e68d14-0422-4eb6-bee2-cf410625d7c0_WhatsApp_Image_2025-07-06_at_18.57.53_ddd9124c.jpg	image	
155	24	uploads/handover/db45b8ff-bcf4-4e1b-908d-5acfdb411939_WhatsApp_Image_2025-07-06_at_18.58.02_df06cad4.jpg		2025-07-06 20:15:06.494981	uploads/handover/db45b8ff-bcf4-4e1b-908d-5acfdb411939_WhatsApp_Image_2025-07-06_at_18.58.02_df06cad4.jpg	image	
156	24	uploads/handover/a2e70954-2e0a-4e63-b4ad-f2aa8005cac4_WhatsApp_Image_2025-07-06_at_18.58.10_db87a8cd.jpg		2025-07-06 20:15:06.494982	uploads/handover/a2e70954-2e0a-4e63-b4ad-f2aa8005cac4_WhatsApp_Image_2025-07-06_at_18.58.10_db87a8cd.jpg	image	
157	24	uploads/handover/8413b2e3-a026-4522-9931-be62bfdb8f89_WhatsApp_Image_2025-07-06_at_18.58.18_516d7087.jpg		2025-07-06 20:15:06.494983	uploads/handover/8413b2e3-a026-4522-9931-be62bfdb8f89_WhatsApp_Image_2025-07-06_at_18.58.18_516d7087.jpg	image	
225	27	uploads/handover/51297abe-28e3-40ce-84d3-c122c30d52a0_IMG_4971.jpeg		2025-07-08 20:33:25.936411	uploads/handover/51297abe-28e3-40ce-84d3-c122c30d52a0_IMG_4971.jpeg	image	
158	24	uploads/handover/f16c678e-92d4-4ef7-8498-13e2fe36b17f_WhatsApp_Image_2025-07-06_at_18.58.31_53f53173.jpg		2025-07-06 20:15:06.494983	uploads/handover/f16c678e-92d4-4ef7-8498-13e2fe36b17f_WhatsApp_Image_2025-07-06_at_18.58.31_53f53173.jpg	image	
159	24	uploads/handover/b6503e3b-c828-436a-896c-211df0dbed7c_WhatsApp_Image_2025-07-06_at_18.58.39_56db1dc1.jpg		2025-07-06 20:15:06.494984	uploads/handover/b6503e3b-c828-436a-896c-211df0dbed7c_WhatsApp_Image_2025-07-06_at_18.58.39_56db1dc1.jpg	image	
160	24	uploads/handover/3cea1e9b-40ef-43d8-b444-76cb06fcfc38_WhatsApp_Image_2025-07-06_at_18.59.07_7f88a456.jpg		2025-07-06 20:15:06.494984	uploads/handover/3cea1e9b-40ef-43d8-b444-76cb06fcfc38_WhatsApp_Image_2025-07-06_at_18.59.07_7f88a456.jpg	image	
161	24	uploads/handover/4b2879ae-7d41-4cb2-ab83-4fa1d96de62b_WhatsApp_Image_2025-07-06_at_18.59.30_b82c64e4.jpg		2025-07-06 20:15:06.494985	uploads/handover/4b2879ae-7d41-4cb2-ab83-4fa1d96de62b_WhatsApp_Image_2025-07-06_at_18.59.30_b82c64e4.jpg	image	
162	24	uploads/handover/90008e17-705d-4912-8dc8-fb26a0b061cc_WhatsApp_Image_2025-07-06_at_18.59.40_3f7f384e.jpg		2025-07-06 20:15:06.494985	uploads/handover/90008e17-705d-4912-8dc8-fb26a0b061cc_WhatsApp_Image_2025-07-06_at_18.59.40_3f7f384e.jpg	image	
163	24	uploads/handover/23bf287a-de48-4f31-9c76-37978d800442_WhatsApp_Image_2025-07-06_at_19.00.06_9d2160d4.jpg		2025-07-06 20:15:06.494986	uploads/handover/23bf287a-de48-4f31-9c76-37978d800442_WhatsApp_Image_2025-07-06_at_19.00.06_9d2160d4.jpg	image	
164	24	uploads/handover/d6e7b8cb-77c9-4510-9c4b-f27711240711_WhatsApp_Image_2025-07-06_at_19.00.14_783b008e.jpg		2025-07-06 20:15:06.494986	uploads/handover/d6e7b8cb-77c9-4510-9c4b-f27711240711_WhatsApp_Image_2025-07-06_at_19.00.14_783b008e.jpg	image	
165	24	uploads/handover/16936b77-9f6a-417e-8b34-d0c5d81b82b0_WhatsApp_Image_2025-07-06_at_19.00.27_310ba63d.jpg		2025-07-06 20:15:06.494987	uploads/handover/16936b77-9f6a-417e-8b34-d0c5d81b82b0_WhatsApp_Image_2025-07-06_at_19.00.27_310ba63d.jpg	image	
166	24	uploads/handover/df60a33e-ba39-413f-93a1-879ba08cf452_WhatsApp_Image_2025-07-06_at_19.00.35_f59dddb8.jpg		2025-07-06 20:15:06.494987	uploads/handover/df60a33e-ba39-413f-93a1-879ba08cf452_WhatsApp_Image_2025-07-06_at_19.00.35_f59dddb8.jpg	image	
167	24	uploads/handover/4c9c50dc-00e6-40d4-a042-00a90f684d9c_WhatsApp_Image_2025-07-06_at_19.00.42_04a418dd.jpg		2025-07-06 20:15:06.494988	uploads/handover/4c9c50dc-00e6-40d4-a042-00a90f684d9c_WhatsApp_Image_2025-07-06_at_19.00.42_04a418dd.jpg	image	
168	24	uploads/handover/d6a608db-8e35-491a-b002-9691dfc4f45f_WhatsApp_Image_2025-07-06_at_19.00.50_5fa40888.jpg		2025-07-06 20:15:06.494988	uploads/handover/d6a608db-8e35-491a-b002-9691dfc4f45f_WhatsApp_Image_2025-07-06_at_19.00.50_5fa40888.jpg	image	
169	25	uploads/handover/e4ab30c2-3abc-4cf9-b4da-84d9429351d1_WhatsApp_Image_2025-07-06_at_18.57.10_8dea943a.jpg		2025-07-07 22:58:44.000245	uploads/handover/e4ab30c2-3abc-4cf9-b4da-84d9429351d1_WhatsApp_Image_2025-07-06_at_18.57.10_8dea943a.jpg	image	
170	25	uploads/handover/8b28026a-53be-49b8-bdd6-411479b0223d_WhatsApp_Image_2025-07-06_at_18.57.19_984ad30f.jpg		2025-07-07 22:58:44.000255	uploads/handover/8b28026a-53be-49b8-bdd6-411479b0223d_WhatsApp_Image_2025-07-06_at_18.57.19_984ad30f.jpg	image	
171	25	uploads/handover/786e5ce7-8ff2-45f9-9888-7d953a60621f_WhatsApp_Image_2025-07-06_at_18.57.35_21285158.jpg		2025-07-07 22:58:44.000256	uploads/handover/786e5ce7-8ff2-45f9-9888-7d953a60621f_WhatsApp_Image_2025-07-06_at_18.57.35_21285158.jpg	image	
172	25	uploads/handover/4d335e9e-bee6-4773-b438-74ef0e52317e_WhatsApp_Image_2025-07-06_at_18.57.35_a014f68a.jpg		2025-07-07 22:58:44.000257	uploads/handover/4d335e9e-bee6-4773-b438-74ef0e52317e_WhatsApp_Image_2025-07-06_at_18.57.35_a014f68a.jpg	image	
173	25	uploads/handover/ffa003f6-aa0c-48f0-896f-c98b5a2a3472_WhatsApp_Image_2025-07-06_at_18.57.53_ddd9124c.jpg		2025-07-07 22:58:44.000257	uploads/handover/ffa003f6-aa0c-48f0-896f-c98b5a2a3472_WhatsApp_Image_2025-07-06_at_18.57.53_ddd9124c.jpg	image	
174	25	uploads/handover/c6d9751d-da6a-4a52-8cad-9802a4bc168e_WhatsApp_Image_2025-07-06_at_18.58.02_df06cad4.jpg		2025-07-07 22:58:44.000257	uploads/handover/c6d9751d-da6a-4a52-8cad-9802a4bc168e_WhatsApp_Image_2025-07-06_at_18.58.02_df06cad4.jpg	image	
175	25	uploads/handover/7e6accc8-7893-4d87-b977-9c1b4b3cd711_WhatsApp_Image_2025-07-06_at_18.58.10_db87a8cd.jpg		2025-07-07 22:58:44.000258	uploads/handover/7e6accc8-7893-4d87-b977-9c1b4b3cd711_WhatsApp_Image_2025-07-06_at_18.58.10_db87a8cd.jpg	image	
176	25	uploads/handover/0e6cd241-1b87-4919-a136-0b6c618547d1_WhatsApp_Image_2025-07-06_at_18.58.18_516d7087.jpg		2025-07-07 22:58:44.000258	uploads/handover/0e6cd241-1b87-4919-a136-0b6c618547d1_WhatsApp_Image_2025-07-06_at_18.58.18_516d7087.jpg	image	
177	26	uploads/handover/acf8ff9c-580b-4a52-a875-bcaeceb3ba40_7abbb8ad-da19-41f1-aadd-29aaee5f2968.jpeg		2025-07-07 23:56:23.092246	uploads/handover/acf8ff9c-580b-4a52-a875-bcaeceb3ba40_7abbb8ad-da19-41f1-aadd-29aaee5f2968.jpeg	image	
178	26	uploads/handover/d84e7a4e-8eaa-4bc9-b916-c3c0b46aef7e_c75006dc-dd9b-486f-ba12-ac1228a5534e.jpeg		2025-07-07 23:56:23.09225	uploads/handover/d84e7a4e-8eaa-4bc9-b916-c3c0b46aef7e_c75006dc-dd9b-486f-ba12-ac1228a5534e.jpeg	image	
179	26	uploads/handover/edf4bc6a-c4cc-45d9-bbae-22fe5a872d8b_48f688ef-d7f3-4b28-b050-7d27b06c109c.jpeg		2025-07-07 23:56:23.092252	uploads/handover/edf4bc6a-c4cc-45d9-bbae-22fe5a872d8b_48f688ef-d7f3-4b28-b050-7d27b06c109c.jpeg	image	
180	26	uploads/handover/1e753ddd-eae8-4da9-833f-3f9c076592f8_ea8637f7-9d08-4fa7-b4b0-daa45baeb6f1.jpeg		2025-07-07 23:56:23.092252	uploads/handover/1e753ddd-eae8-4da9-833f-3f9c076592f8_ea8637f7-9d08-4fa7-b4b0-daa45baeb6f1.jpeg	image	
181	26	uploads/handover/0e98384c-ab90-4727-a71f-5797445aaee2_645e5f8f-0316-4cd9-b9fa-35aef10e153d.jpeg		2025-07-07 23:56:23.092253	uploads/handover/0e98384c-ab90-4727-a71f-5797445aaee2_645e5f8f-0316-4cd9-b9fa-35aef10e153d.jpeg	image	
182	26	uploads/handover/fb1037fe-3939-446e-bb38-816e2210d4d2_9355e4d8-4236-42c3-a7c5-338bedae0ce3.jpeg		2025-07-07 23:56:23.092253	uploads/handover/fb1037fe-3939-446e-bb38-816e2210d4d2_9355e4d8-4236-42c3-a7c5-338bedae0ce3.jpeg	image	
183	26	uploads/handover/e99486ba-cb49-4be6-8857-6754f96af5a1_d960f4ad-ac07-432d-99b0-031039191d53.jpeg		2025-07-07 23:56:23.092254	uploads/handover/e99486ba-cb49-4be6-8857-6754f96af5a1_d960f4ad-ac07-432d-99b0-031039191d53.jpeg	image	
184	26	uploads/handover/eb6d1400-6b4c-43e9-be7d-7e47e179c6e1_d2fbd26a-4150-4eae-b6c4-1b70cc5f75af.jpeg		2025-07-07 23:56:23.092254	uploads/handover/eb6d1400-6b4c-43e9-be7d-7e47e179c6e1_d2fbd26a-4150-4eae-b6c4-1b70cc5f75af.jpeg	image	
185	26	uploads/handover/cf8ae8b2-9b06-4f45-ab17-a7ff36ad76db_298e77ec-2675-4571-8a7b-3f6098873b26.jpeg		2025-07-07 23:56:23.092255	uploads/handover/cf8ae8b2-9b06-4f45-ab17-a7ff36ad76db_298e77ec-2675-4571-8a7b-3f6098873b26.jpeg	image	
186	26	uploads/handover/94489c01-7366-4568-9d73-71a32306a6f5_285807c0-a577-4ad1-8701-5f02d925c857.jpeg		2025-07-07 23:56:23.092255	uploads/handover/94489c01-7366-4568-9d73-71a32306a6f5_285807c0-a577-4ad1-8701-5f02d925c857.jpeg	image	
187	26	uploads/handover/e78174ee-161b-476e-8b66-8061b214365f_967ff901-6f35-4af4-9381-1d975c460bd9.jpeg		2025-07-07 23:56:23.092255	uploads/handover/e78174ee-161b-476e-8b66-8061b214365f_967ff901-6f35-4af4-9381-1d975c460bd9.jpeg	image	
188	26	uploads/handover/e6168f47-5c11-4a86-9048-516ef0f2e5e5_d4358cb5-5a45-436b-89ec-e5aaa6a9e335.jpeg		2025-07-07 23:56:23.092256	uploads/handover/e6168f47-5c11-4a86-9048-516ef0f2e5e5_d4358cb5-5a45-436b-89ec-e5aaa6a9e335.jpeg	image	
189	26	uploads/handover/f80221ed-5f9a-43e6-9fb6-763c1f556f04_67ecead5-9418-49ec-834c-abc98a306783.jpeg		2025-07-07 23:56:23.092256	uploads/handover/f80221ed-5f9a-43e6-9fb6-763c1f556f04_67ecead5-9418-49ec-834c-abc98a306783.jpeg	image	
190	26	uploads/handover/7c3a702d-4e1e-456b-8eb6-90a736e9bf0f_61029d48-fdc8-46f2-861d-9ede331742b9.jpeg		2025-07-07 23:56:23.092256	uploads/handover/7c3a702d-4e1e-456b-8eb6-90a736e9bf0f_61029d48-fdc8-46f2-861d-9ede331742b9.jpeg	image	
191	26	uploads/handover/50bc05ff-cf79-423f-91f1-034600338b47_056da6e6-78b2-408b-be37-28bd34f55cd6.jpeg		2025-07-07 23:56:23.092257	uploads/handover/50bc05ff-cf79-423f-91f1-034600338b47_056da6e6-78b2-408b-be37-28bd34f55cd6.jpeg	image	
192	26	uploads/handover/dcdbb6fd-29e5-4971-970b-dcdec90bf713_6f15ce79-f597-4c58-97f1-b65a274e7416.jpeg		2025-07-07 23:56:23.092257	uploads/handover/dcdbb6fd-29e5-4971-970b-dcdec90bf713_6f15ce79-f597-4c58-97f1-b65a274e7416.jpeg	image	
193	26	uploads/handover/f273dec7-3b24-4ac4-b608-66b3bd75fdd0_60c6cca1-d3bc-4f08-911d-9edba021ac34.jpeg		2025-07-07 23:56:23.092257	uploads/handover/f273dec7-3b24-4ac4-b608-66b3bd75fdd0_60c6cca1-d3bc-4f08-911d-9edba021ac34.jpeg	image	
194	26	uploads/handover/74562152-3678-4848-ae30-c07c552a26b7_1cfb6e9e-5b8d-4e08-88ce-f0b8786ef01d.jpeg		2025-07-07 23:56:23.092258	uploads/handover/74562152-3678-4848-ae30-c07c552a26b7_1cfb6e9e-5b8d-4e08-88ce-f0b8786ef01d.jpeg	image	
195	26	uploads/handover/9527c8e6-be83-4568-a76d-89787280515b_4a08db95-a0e4-4b12-a1dd-f88731bf2343.jpeg		2025-07-07 23:56:23.092258	uploads/handover/9527c8e6-be83-4568-a76d-89787280515b_4a08db95-a0e4-4b12-a1dd-f88731bf2343.jpeg	image	
196	26	uploads/handover/e10cefea-fda1-43fd-8c12-e591c8e212a2_63d751f3-7fab-4f76-a3b5-1739f1c7ee11.jpeg		2025-07-07 23:56:23.092259	uploads/handover/e10cefea-fda1-43fd-8c12-e591c8e212a2_63d751f3-7fab-4f76-a3b5-1739f1c7ee11.jpeg	image	
197	26	uploads/handover/08eab34e-4b1e-422f-9a08-b791afb0655f_6fcbb279-9126-469d-84ca-2237c6104255.jpeg		2025-07-07 23:56:23.092259	uploads/handover/08eab34e-4b1e-422f-9a08-b791afb0655f_6fcbb279-9126-469d-84ca-2237c6104255.jpeg	image	
198	26	uploads/handover/12f2b523-3262-4b7e-b719-2d1e42108a38_1969bf58-2f97-49b9-8ac7-caaa5987b1ff.jpeg		2025-07-07 23:56:23.092259	uploads/handover/12f2b523-3262-4b7e-b719-2d1e42108a38_1969bf58-2f97-49b9-8ac7-caaa5987b1ff.jpeg	image	
199	26	uploads/handover/d6234640-4b6e-4e63-9420-c9cacb89ddad_2fe1016f-6c3d-40f6-a440-da30f6fd8bc7.jpeg		2025-07-07 23:56:23.09226	uploads/handover/d6234640-4b6e-4e63-9420-c9cacb89ddad_2fe1016f-6c3d-40f6-a440-da30f6fd8bc7.jpeg	image	
200	26	uploads/handover/d196e13f-85ed-4a60-89eb-9c265dbef00d_1821822b-b9dd-4fe7-8f83-18e4622b17de.jpeg		2025-07-07 23:56:23.09226	uploads/handover/d196e13f-85ed-4a60-89eb-9c265dbef00d_1821822b-b9dd-4fe7-8f83-18e4622b17de.jpeg	image	
201	26	uploads/handover/255ca85b-7501-452c-b36b-cdb96ba997f4_69be770d-42f9-4c55-a10c-c778b406e8d9.jpeg		2025-07-07 23:56:23.09226	uploads/handover/255ca85b-7501-452c-b36b-cdb96ba997f4_69be770d-42f9-4c55-a10c-c778b406e8d9.jpeg	image	
202	27	uploads/handover/6b72357d-6ee4-4e0d-a4be-5d9c38d088b3_IMG_4993.jpeg		2025-07-08 20:33:25.936392	uploads/handover/6b72357d-6ee4-4e0d-a4be-5d9c38d088b3_IMG_4993.jpeg	image	
203	27	uploads/handover/bab11b0e-c302-4d97-a3f6-33da62ec9d0b_IMG_4991.jpeg		2025-07-08 20:33:25.936397	uploads/handover/bab11b0e-c302-4d97-a3f6-33da62ec9d0b_IMG_4991.jpeg	image	
204	27	uploads/handover/7c192161-90ce-4389-901e-c6b6f78e56bf_IMG_4990.jpeg		2025-07-08 20:33:25.936398	uploads/handover/7c192161-90ce-4389-901e-c6b6f78e56bf_IMG_4990.jpeg	image	
205	27	uploads/handover/421b236c-03ac-4326-b25d-8691482169cf_IMG_4978.jpeg		2025-07-08 20:33:25.936399	uploads/handover/421b236c-03ac-4326-b25d-8691482169cf_IMG_4978.jpeg	image	
206	27	uploads/handover/febf767f-cd96-4a6c-9bcf-d34945e619f6_IMG_4992.jpeg		2025-07-08 20:33:25.936399	uploads/handover/febf767f-cd96-4a6c-9bcf-d34945e619f6_IMG_4992.jpeg	image	
207	27	uploads/handover/3feff101-354e-488a-9843-1089a9bda29e_IMG_4984.jpeg		2025-07-08 20:33:25.9364	uploads/handover/3feff101-354e-488a-9843-1089a9bda29e_IMG_4984.jpeg	image	
208	27	uploads/handover/c86d9f8b-1577-436e-b3d0-02adaa240e4a_IMG_4983.jpeg		2025-07-08 20:33:25.936401	uploads/handover/c86d9f8b-1577-436e-b3d0-02adaa240e4a_IMG_4983.jpeg	image	
209	27	uploads/handover/5fcfc28f-1265-436b-82cd-e5a6c201072b_B04E5C23-B204-4812-864E-5D84010E3565.jpeg		2025-07-08 20:33:25.936401	uploads/handover/5fcfc28f-1265-436b-82cd-e5a6c201072b_B04E5C23-B204-4812-864E-5D84010E3565.jpeg	image	
210	27	uploads/handover/2a400adc-8c7b-4683-b686-7ae24cd346a9_C00F6C50-3AC7-445F-9E63-BDAE9520A89C.jpeg		2025-07-08 20:33:25.936402	uploads/handover/2a400adc-8c7b-4683-b686-7ae24cd346a9_C00F6C50-3AC7-445F-9E63-BDAE9520A89C.jpeg	image	
211	27	uploads/handover/74a74777-530e-4d53-b907-f7b874f9d2eb_6A8B401D-1113-4B97-8064-B2869CEB75DB.jpeg		2025-07-08 20:33:25.936403	uploads/handover/74a74777-530e-4d53-b907-f7b874f9d2eb_6A8B401D-1113-4B97-8064-B2869CEB75DB.jpeg	image	
212	27	uploads/handover/7794ab0a-99f8-491e-bdd8-7e1814c0ff1a_D97D39E1-8F05-43BE-BC51-D07DDEA72FAB.jpeg		2025-07-08 20:33:25.936403	uploads/handover/7794ab0a-99f8-491e-bdd8-7e1814c0ff1a_D97D39E1-8F05-43BE-BC51-D07DDEA72FAB.jpeg	image	
213	27	uploads/handover/1c26833f-ecfc-4cee-9272-be4577257f8f_IMG_4977.png		2025-07-08 20:33:25.936404	uploads/handover/1c26833f-ecfc-4cee-9272-be4577257f8f_IMG_4977.png	image	
214	27	uploads/handover/9ef5d6f0-5f51-4b9a-8b3a-bb7d4585cedb_8E08B262-0A28-4B02-9AA7-E3DE40D5764D.jpeg		2025-07-08 20:33:25.936404	uploads/handover/9ef5d6f0-5f51-4b9a-8b3a-bb7d4585cedb_8E08B262-0A28-4B02-9AA7-E3DE40D5764D.jpeg	image	
215	27	uploads/handover/3e7e0147-ed80-40da-98f2-d790fc7178b0_IMG_4975.jpeg		2025-07-08 20:33:25.936405	uploads/handover/3e7e0147-ed80-40da-98f2-d790fc7178b0_IMG_4975.jpeg	image	
216	27	uploads/handover/c5a6665a-8e2d-41ab-b108-e517b75517b3_IMG_4953.jpeg		2025-07-08 20:33:25.936405	uploads/handover/c5a6665a-8e2d-41ab-b108-e517b75517b3_IMG_4953.jpeg	image	
217	27	uploads/handover/510b0da9-5e40-4a56-937f-8dbb3d530cb5_IMG_4951.jpeg		2025-07-08 20:33:25.936406	uploads/handover/510b0da9-5e40-4a56-937f-8dbb3d530cb5_IMG_4951.jpeg	image	
218	27	uploads/handover/7e93a499-b1d9-4c5c-82d2-f43e226720c4_IMG_4989.png		2025-07-08 20:33:25.936407	uploads/handover/7e93a499-b1d9-4c5c-82d2-f43e226720c4_IMG_4989.png	image	
219	27	uploads/handover/5aa395d6-a4ad-4062-a104-7f940b95538b_IMG_4974.jpeg		2025-07-08 20:33:25.936407	uploads/handover/5aa395d6-a4ad-4062-a104-7f940b95538b_IMG_4974.jpeg	image	
220	27	uploads/handover/b8a1cc69-5e3e-40e3-9b43-12017656e5b9_IMG_4950.jpeg		2025-07-08 20:33:25.936408	uploads/handover/b8a1cc69-5e3e-40e3-9b43-12017656e5b9_IMG_4950.jpeg	image	
221	27	uploads/handover/0a582a91-83f0-4d40-8baf-57558feb6b02_IMG_4985.png		2025-07-08 20:33:25.936409	uploads/handover/0a582a91-83f0-4d40-8baf-57558feb6b02_IMG_4985.png	image	
222	27	uploads/handover/8ec259bd-6df7-42bb-9e4e-3712022404c3_IMG_4970.jpeg		2025-07-08 20:33:25.936409	uploads/handover/8ec259bd-6df7-42bb-9e4e-3712022404c3_IMG_4970.jpeg	image	
223	27	uploads/handover/3b1b4955-058d-4cb3-a6b5-b4150919f70d_IMG_4968.jpeg		2025-07-08 20:33:25.93641	uploads/handover/3b1b4955-058d-4cb3-a6b5-b4150919f70d_IMG_4968.jpeg	image	
224	27	uploads/handover/dc512e2a-7251-4bf5-8157-244c31bda6a6_IMG_4969.jpeg		2025-07-08 20:33:25.93641	uploads/handover/dc512e2a-7251-4bf5-8157-244c31bda6a6_IMG_4969.jpeg	image	
226	28	uploads/handover/c065926e-c6e4-4b17-bda4-c25c1b4ee854_WhatsApp_Image_2025-07-06_at_18.57.10_8dea943a.jpg		2025-07-08 21:03:16.879701	uploads/handover/c065926e-c6e4-4b17-bda4-c25c1b4ee854_WhatsApp_Image_2025-07-06_at_18.57.10_8dea943a.jpg	image	
227	28	uploads/handover/9dc61131-810a-4eef-9131-b6e525e20594_WhatsApp_Image_2025-07-06_at_18.57.19_984ad30f.jpg		2025-07-08 21:03:16.879707	uploads/handover/9dc61131-810a-4eef-9131-b6e525e20594_WhatsApp_Image_2025-07-06_at_18.57.19_984ad30f.jpg	image	
228	28	uploads/handover/7798527f-4aa7-43ed-b7bb-646e0c230e70_WhatsApp_Image_2025-07-06_at_18.57.35_21285158.jpg		2025-07-08 21:03:16.879708	uploads/handover/7798527f-4aa7-43ed-b7bb-646e0c230e70_WhatsApp_Image_2025-07-06_at_18.57.35_21285158.jpg	image	
229	28	uploads/handover/0fe56244-cd6f-4861-af5b-fe69b66a1bd6_WhatsApp_Image_2025-07-06_at_18.57.35_a014f68a.jpg		2025-07-08 21:03:16.879708	uploads/handover/0fe56244-cd6f-4861-af5b-fe69b66a1bd6_WhatsApp_Image_2025-07-06_at_18.57.35_a014f68a.jpg	image	
230	28	uploads/handover/84cd968a-669c-49c6-ba4d-28dacdd6526d_WhatsApp_Image_2025-07-06_at_18.57.53_ddd9124c.jpg		2025-07-08 21:03:16.879709	uploads/handover/84cd968a-669c-49c6-ba4d-28dacdd6526d_WhatsApp_Image_2025-07-06_at_18.57.53_ddd9124c.jpg	image	
231	28	uploads/handover/13d05059-0372-4d0a-813a-c7228f8e0f02_WhatsApp_Image_2025-07-06_at_18.58.02_df06cad4.jpg		2025-07-08 21:03:16.87971	uploads/handover/13d05059-0372-4d0a-813a-c7228f8e0f02_WhatsApp_Image_2025-07-06_at_18.58.02_df06cad4.jpg	image	
232	28	uploads/handover/13bc3382-1984-4bc2-b763-2614d25ae6b7_WhatsApp_Image_2025-07-06_at_18.58.10_db87a8cd.jpg		2025-07-08 21:03:16.87971	uploads/handover/13bc3382-1984-4bc2-b763-2614d25ae6b7_WhatsApp_Image_2025-07-06_at_18.58.10_db87a8cd.jpg	image	
233	28	uploads/handover/a17cfbd9-c1db-4419-964e-c2e586e5d71d_WhatsApp_Image_2025-07-06_at_18.58.18_516d7087.jpg		2025-07-08 21:03:16.879711	uploads/handover/a17cfbd9-c1db-4419-964e-c2e586e5d71d_WhatsApp_Image_2025-07-06_at_18.58.18_516d7087.jpg	image	
234	28	uploads/handover/aed649c3-b26c-4bbf-8524-e57a53a210b9_WhatsApp_Image_2025-07-06_at_18.58.31_53f53173.jpg		2025-07-08 21:03:16.879711	uploads/handover/aed649c3-b26c-4bbf-8524-e57a53a210b9_WhatsApp_Image_2025-07-06_at_18.58.31_53f53173.jpg	image	
235	28	uploads/handover/8bd9f5a7-3e15-46bc-bc9b-57c8bdd6d39a_WhatsApp_Image_2025-07-06_at_18.58.39_56db1dc1.jpg		2025-07-08 21:03:16.879712	uploads/handover/8bd9f5a7-3e15-46bc-bc9b-57c8bdd6d39a_WhatsApp_Image_2025-07-06_at_18.58.39_56db1dc1.jpg	image	
236	28	uploads/handover/f37bd12d-c050-4f0c-a4ac-1a2985b65c47_WhatsApp_Image_2025-07-06_at_18.59.07_7f88a456.jpg		2025-07-08 21:03:16.879712	uploads/handover/f37bd12d-c050-4f0c-a4ac-1a2985b65c47_WhatsApp_Image_2025-07-06_at_18.59.07_7f88a456.jpg	image	
237	28	uploads/handover/e4bce607-6230-48c4-b360-e4b16bc49f43_WhatsApp_Image_2025-07-06_at_18.59.30_b82c64e4.jpg		2025-07-08 21:03:16.879713	uploads/handover/e4bce607-6230-48c4-b360-e4b16bc49f43_WhatsApp_Image_2025-07-06_at_18.59.30_b82c64e4.jpg	image	
238	28	uploads/handover/b0618f47-239d-4aef-ba60-885558b44572_WhatsApp_Image_2025-07-06_at_18.59.40_3f7f384e.jpg		2025-07-08 21:03:16.879714	uploads/handover/b0618f47-239d-4aef-ba60-885558b44572_WhatsApp_Image_2025-07-06_at_18.59.40_3f7f384e.jpg	image	
239	28	uploads/handover/00fafe38-261a-4cdf-84f6-9d3a2435c9b3_WhatsApp_Image_2025-07-06_at_19.00.06_9d2160d4.jpg		2025-07-08 21:03:16.879714	uploads/handover/00fafe38-261a-4cdf-84f6-9d3a2435c9b3_WhatsApp_Image_2025-07-06_at_19.00.06_9d2160d4.jpg	image	
240	28	uploads/handover/d165da7a-5fd7-44d4-86f1-c0c64f6ec12b_WhatsApp_Image_2025-07-06_at_19.00.14_783b008e.jpg		2025-07-08 21:03:16.879715	uploads/handover/d165da7a-5fd7-44d4-86f1-c0c64f6ec12b_WhatsApp_Image_2025-07-06_at_19.00.14_783b008e.jpg	image	
241	28	uploads/handover/f0d7be8f-e61a-4f33-925d-7863997e4037_WhatsApp_Image_2025-07-06_at_19.00.27_310ba63d.jpg		2025-07-08 21:03:16.879715	uploads/handover/f0d7be8f-e61a-4f33-925d-7863997e4037_WhatsApp_Image_2025-07-06_at_19.00.27_310ba63d.jpg	image	
242	28	uploads/handover/963ad571-a1d3-4cd6-b4f2-1aa536e4b513_WhatsApp_Image_2025-07-06_at_19.00.35_f59dddb8.jpg		2025-07-08 21:03:16.879716	uploads/handover/963ad571-a1d3-4cd6-b4f2-1aa536e4b513_WhatsApp_Image_2025-07-06_at_19.00.35_f59dddb8.jpg	image	
243	28	uploads/handover/934f9565-2346-495c-92c0-8c1fb4873a5b_WhatsApp_Image_2025-07-06_at_19.00.42_04a418dd.jpg		2025-07-08 21:03:16.879716	uploads/handover/934f9565-2346-495c-92c0-8c1fb4873a5b_WhatsApp_Image_2025-07-06_at_19.00.42_04a418dd.jpg	image	
244	28	uploads/handover/38ace494-5f66-4507-9dff-5519f786aab5_WhatsApp_Image_2025-07-06_at_19.00.50_5fa40888.jpg		2025-07-08 21:03:16.879717	uploads/handover/38ace494-5f66-4507-9dff-5519f786aab5_WhatsApp_Image_2025-07-06_at_19.00.50_5fa40888.jpg	image	
\.


--
-- Data for Name: vehicle_maintenance; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_maintenance (id, vehicle_id, date, maintenance_type, description, status, cost, technician, parts_replaced, actions_taken, notes, created_at, updated_at, receipt_image_url, delivery_receipt_url, pickup_receipt_url) FROM stdin;
4	23	2025-07-06	دورية	وصف	قيد التنفيذ	0	محمد محمد محمد	وصف	وصف	وصف	2025-07-06 12:09:22.45657	2025-07-06 12:09:22.456575	https://d72f2aef-918c-4148-9723-15870f8c7cf6-00-2c1ygyxvqoldk.riker.replit.dev/mobile/vehicles/maintenance/add?vehicle_id=5	https://d72f2aef-918c-4148-9723-15870f8c7cf6-00-2c1ygyxvqoldk.riker.replit.dev/mobile/vehicles/maintenance/add?vehicle_id=5	https://d72f2aef-918c-4148-9723-15870f8c7cf6-00-2c1ygyxvqoldk.riker.replit.dev/mobile/vehicles/maintenance/add?vehicle_id=5
\.


--
-- Data for Name: vehicle_maintenance_image; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_maintenance_image (id, maintenance_id, image_path, image_type, uploaded_at) FROM stdin;
\.


--
-- Data for Name: vehicle_periodic_inspection; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_periodic_inspection (id, vehicle_id, inspection_date, expiry_date, inspection_number, inspector_name, inspection_type, inspection_status, cost, results, recommendations, certificate_file, notes, created_at, updated_at, inspection_center, result, driver_name, supervisor_name) FROM stdin;
5	12	2025-05-01	2023-01-01	الوكالة	شركة الجزيرة 	periodic	valid	0	سليم وكالة		\N		2025-05-15 13:41:44.753948	2025-05-15 13:41:44.753952	الوكالة	periodic	\N	شركة الجزيرة 
\.


--
-- Data for Name: vehicle_project; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_project (id, vehicle_id, project_name, location, manager_name, start_date, end_date, is_active, notes, created_at, updated_at) FROM stdin;
2	17	 ارامكس	القصيم بريدة	ارامكس	2025-04-27	\N	t		2025-04-27 21:25:42.753056	2025-04-27 21:25:42.753061
3	12	ارامكس 	Qassim	عيسى القحطاني	2025-04-29	\N	t		2025-04-29 23:04:12.29157	2025-04-29 23:22:37.816967
4	14	ارامكس	القصيم بريدة	ارامكس	2025-05-18	2027-12-30	t		2025-05-18 21:03:32.812846	2025-05-18 21:03:32.81285
\.


--
-- Data for Name: vehicle_rental; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_rental (id, vehicle_id, start_date, end_date, monthly_cost, is_active, lessor_name, lessor_contact, contract_number, notes, created_at, updated_at, city, company_id) FROM stdin;
2	17	2025-05-22	2025-05-22	555	t					2025-05-22 17:43:12.693326	2025-05-22 17:43:12.693331		\N
\.


--
-- Data for Name: vehicle_safety_check; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_safety_check (id, vehicle_id, check_date, check_type, driver_id, driver_name, supervisor_id, supervisor_name, status, check_form_link, issues_found, issues_description, actions_taken, notes, created_at, updated_at) FROM stdin;
2	12	2025-04-23	monthly	\N	محمد عمرن شوكة علي	\N	زياد الهمداني	completed	https://drive.google.com/file/d/1z9ggwDD5YZJClK-GeKiStLeb7JVdT4VL/view	f				2025-04-23 15:55:24.6529	2025-04-23 15:55:24.652904
3	2	2025-05-29	monthly	\N	وضاح نبيل	\N	زياد الهمداني	completed	https://acrobat.adobe.com/id/urn:aaid:sc:AP:3952acec-6761-4f4f-833f-9cd75ac6f5dd	f		تم اصلاح جميع تلفيات السيارة السياره  بدون تلفيات 		2025-05-29 10:44:34.885717	2025-05-29 10:44:34.885721
4	17	2025-05-31	monthly	\N	عمر عبدالوهاب المغربي 	\N	زياد الهمداني	completed	https://acrobat.adobe.com/id/urn:aaid:sc:AP:620f6ce0-cac5-4d77-baf1-e3f52067b934	f		تم اصلاح جميع التلفيات السيارة بدون تلفيات	السيارة بدون تلفيات 	2025-05-31 11:16:07.368777	2025-05-31 11:16:07.368781
6	11	2025-05-31	monthly	\N	سيف الرحمن محمد ارشد	\N	زياد الهمداني	completed	https://acrobat.adobe.com/id/urn:aaid:sc:AP:06fc80cc-26e9-4924-a68c-46d6d9888e1a	f		تم الانتهاء من كافة التلفيات الموجودة	تم تسليم السيارة لي محمد مبارك بدون تلفيات 	2025-05-31 12:13:25.773688	2025-05-31 12:13:25.773692
7	14	2025-06-30	monthly	\N	محمد عثمات	\N	زياد الهمداني-- تسليم عهدة	completed	https://acrobat.adobe.com/id/urn:aaid:sc:AP:0ddccade-fe3f-4b0d-bbac-9bde7ddc6af5	f		يوجد ضربة جوار باب  خزان الديزل    الصدام الامامي مثبت بي مسامير 	يوجد ضربة جوار باب  خزان الديزل    الصدام الامامي مثبت بي مسامير 	2025-06-30 20:05:02.112775	2025-06-30 20:05:02.112781
8	11	2025-06-30	monthly	\N	محمد مبارك	\N	زياد الهمداني-- تسليم عهدة	completed	https://acrobat.adobe.com/id/urn:aaid:sc:AP:eee4b1b9-3d77-422e-9bc1-c314c5eb5bae	f		يوجد اهتراء في  المرتب الداخلية    تم اصلاح الملاحظات السابقة على المندوب سيف الرحمن    يوجد ضربة اسفل السيارة جهة اليمين جوار الباب السحاب 	يوجد اهتراء في  المرتب الداخلية    تم اصلاح الملاحظات السابقة على المندوب سيف الرحمن    يوجد ضربة اسفل السيارة جهة اليمين جوار الباب السحاب 	2025-06-30 20:28:27.00936	2025-06-30 20:28:27.009364
\.


--
-- Data for Name: vehicle_workshop; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_workshop (id, vehicle_id, entry_date, exit_date, reason, description, repair_status, cost, workshop_name, technician_name, notes, created_at, updated_at, delivery_link, reception_link, status) FROM stdin;
7	10	2025-04-29	2025-05-07	accident	الغرض حادث	completed	0	امان السريع بريدة	مهند		2025-04-30 06:33:25.130975	2025-05-17 10:54:41.567556	https://drive.google.com/file/d/19Ti4pze6-LumDS8Yk3Vi_AotIMdfXZ3F/view?usp=drivesdk	https://drive.google.com/file/d/1FXHB41nrb_dGON4BXCRphcM88xZQw4N7/view?usp=drive_link	in_progress
10	20	2025-05-15	2025-05-18	maintenance	ارتفاع الحرارة----- تم الاصلاح 	completed	0	امان السريع بريدة 	مهند		2025-05-15 06:10:50.796258	2025-05-18 11:15:09.527292	https://drive.google.com/file/d/1KAee54XfZ2c452vdNgI-8-8hS70hR4O6/view?usp=drivesdk	https://drive.google.com/file/d/14stvWxTvj1j0CR9_9gMgcvZ8CYuGCPBw/view?usp=drive_link	in_progress
13	9	2025-05-31	2025-06-03	breakdown	فرامل ومقصات  اذرعه 	completed	0	امان السريع	مهند	\N	2025-06-04 06:55:56.111679	2025-06-23 12:38:21.335551	https://drive.google.com/file/d/1jp8RSmbNCtYkxvacT_BCpP1JBfXDlRlu/view?usp=drive_link	https://drive.google.com/drive/u/2/folders/1XakZpEwBViHY3c4HF-O75yqsp_c9wdVE	in_progress
11	17	2025-05-20	\N	breakdown	خراب في المكيف 	completed	0	امان السريع	مهند		2025-05-22 07:46:53.970734	2025-05-22 17:36:14.471543	https://drive.google.com/file/d/13XSghxcOxAs4Z-M6jmwMU3dtJM2AHE2O/view?usp=drive_link	https://drive.google.com/file/d/1Op4f0qwwypXWE5CU3KXhd6NofUQAWBfl/view?usp=drive_link	in_progress
2	17	2025-03-24	2025-04-27	breakdown	عجز المحرك	completed	0	امان السريع	مهند		2025-04-23 15:40:21.829774	2025-05-22 17:52:38.28626	https://drive.google.com/file/d/1z9ggwDD5YZJClK-GeKiStLeb7JVdT4VL/view	https://drive.google.com/file/d/156c0_kcsalqQmOBFZVhV9GvDHQiecbkB/view	in_progress
12	18	2025-05-26	\N	accident	حادث مروري نسبة الخطاء على السائق محمود   تم خصم الف ريال تبقاء  الف	in_progress	0	بادجت	باجت		2025-05-28 09:24:55.466802	2025-05-28 09:24:55.466807	https://drive.google.com/file/d/1S6etkcVAwJm630B4QH9XEivke8ZRp1k4/view?usp=drive_link	\N	in_progress
26	20	2025-06-25	2025-06-28	maintenance	كمبروسر مكيف 	completed	0		مهند	تم عمل الصينة وتم السيارة  محمد عمران 	2025-06-28 10:40:57.493541	2025-06-28 10:40:57.493546	https://drive.google.com/file/d/1NvofNzifMuH6zZ0Qh5kDLK4dzjwmXmar/view?usp=drive_link	\N	in_progress
4	13	2025-04-25	2025-04-28	maintenance	اصلاح المكيف	completed	0				2025-04-24 19:37:03.745909	2025-04-28 08:02:01.685929			in_progress
3	12	2024-10-03	2025-01-23	breakdown	صيانة دورية	completed	0	امان السريع	مهند	\N	2025-04-23 16:23:15.442588	2025-04-29 22:36:08.073629			in_progress
9	8	2025-05-03	2025-05-11	accident	حادث مروري  نسبة الخطاء على الطرف الثاني 	in_progress	0	امان السريع	ابوعلي 		2025-05-12 12:58:25.943708	2025-05-12 12:58:25.943712	https://drive.google.com/file/d/1s6_5o2S8z00ehXZT49j8oXnfpJN9yBHc/view?usp=drive_link	\N	in_progress
27	10	2025-06-30	\N	maintenance	حادث مروري على دامل	in_progress	0	امان السريع	مهند		2025-06-30 19:58:02.286966	2025-06-30 19:58:02.286971	https://drive.google.com/file/d/19I2xeoaUE1rpCrs4ghVemLJC1srDz1AC/view?usp=drive_link	\N	in_progress
6	7	2025-04-27	2025-05-03	maintenance	عطل عجز في المحرك -مكيف -فرامل	completed	0	امان السريع بريدة	مهند	تم اصلاح العجز الموجود في المحرك  والمكيف    والفرامل 	2025-04-27 21:01:49.043866	2025-05-14 06:40:56.884323	https://drive.google.com/file/d/18iYG40eCalC32byTvQtsU6_qjZFo1mVn/view?usp=drivesdk	https://drive.google.com/file/d/1G5cNxkCta8iHZS5BVU1H0kV8P2FyhqmH/view?usp=drivesdk	in_progress
19	8	2024-01-15	2024-01-20	صيانة دورية	تغيير زيت المحرك وفلتر الهواء	مكتمل	250	\N	\N	\N	\N	\N	\N	\N	in_progress
20	8	2024-02-10	2024-02-12	إصلاح	إصلاح نظام الفرامل	مكتمل	450	\N	\N	\N	\N	\N	\N	\N	in_progress
21	14	2024-03-05	\N	صيانة شاملة	صيانة دورية شاملة	قيد التنفيذ	800	\N	\N	\N	\N	\N	\N	\N	in_progress
22	17	2024-01-25	2024-01-28	إصلاح	تبديل إطارات وضبط زوايا	مكتمل	600	\N	\N	\N	\N	\N	\N	\N	in_progress
25	15	2025-06-22	\N	breakdown	عطل 	in_progress	0	امان السريع	ابوعلي 		2025-06-23 12:31:40.464184	2025-06-23 12:31:40.464188	https://drive.google.com/file/d/1FWU6zs3PQoNQTCyMxq0EglPLsG-5zbiD/view?usp=drive_link	\N	in_progress
33	23	2025-07-07	2025-07-08	maintenance	متكمتكمتكمتكمت	in_progress	0		مهند	متكمتكمتكمت	2025-07-07 22:36:00.196355	2025-07-08 16:22:08.254518	https://acrobat.adobe.com/id/urn:aaid:sc:AP:4243d4fc-2215-41e9-9666-572412c4e2d3		in_progress
28	5	2025-07-02	\N	accident	حادث في مقدمة السيارة نسبة الخطاء على صالح	in_progress	2000	امان السريع	مهند		2025-07-02 14:30:57.112338	2025-07-02 14:30:57.112342	https://drive.google.com/file/d/1YFWhHF38GBV0XYuoXze3hWllU3KrbwLl/view?usp=drive_link	\N	in_progress
32	7	2025-07-15	2025-07-16	maintenance	وصف	completed	1400	السلام	محمد محمد	ملاحضة	2025-07-06 12:26:04.40354	2025-07-06 12:26:04.403546	\N	\N	in_progress
23	7	2025-06-10	\N	breakdown	عجز في المحرك	completed	0	امان السريع بريدة	مهند	السياره متعطله عجز في المحرك	2025-06-10 17:36:10.038923	2025-07-03 16:50:24.105129	https://drive.google.com/file/d/1WBeT9jGXbRfkBdBc2YuF1zBIrZ8chmUX/view?usp=drivesdk	https://drive.google.com/file/d/1qVgCuJxqIgj3VrSebSMP3zOLXApjLETd/view?usp=drive_link	in_progress
29	7	2025-07-05	\N	maintenance	صيانة  امان حائل حرارة 	in_progress	123456	امان السريع			2025-07-05 13:44:56.460395	2025-07-05 13:44:56.460399	https://drive.google.com/file/d/1hbw2fKU02RLjdqcRaCx-ez9u0dWe6Lir/view?usp=drive_link	\N	in_progress
24	7	2025-06-22	2025-06-22	maintenance	عجز في المحرك	in_progress	0	امان السريع بريدة	مهند		2025-06-22 11:05:09.968746	2025-07-06 08:44:01.300807			in_progress
30	7	2025-06-29	2025-07-03	maintenance	طلعة السيارة من الورشة ----- بدون تغير كفرات وترصيص	completed	0	امان السريع- بريدة 	مهند		2025-07-06 09:13:10.083952	2025-07-06 09:13:10.083957	https://drive.google.com/file/d/14qqYwktGJxlvSNor4ygIsxfxXLuDfwFp/view?usp=drive_link	\N	in_progress
35	23	2025-07-07	\N	maintenance	اختبار تجريبي من النظام	in_progress	500	ورشة الاختبار	فني الاختبار	سجل تجريبي للاختبار - تم إنشاؤه تلقائياً	2025-07-07 22:52:02.061911	2025-07-07 22:52:02.061913	https://example.com/delivery	https://example.com/pickup	in_progress
36	23	2025-07-07	\N	maintenance	اختبار تجريبي من النظام	in_progress	500	ورشة الاختبار	فني الاختبار	سجل تجريبي للاختبار - تم إنشاؤه تلقائياً	2025-07-07 22:52:02.864701	2025-07-07 22:52:02.864704	https://example.com/delivery	https://example.com/pickup	in_progress
37	23	2025-07-07	\N	maintenance	اختبار تجريبي من النظام	in_progress	500	ورشة الاختبار	فني الاختبار	سجل تجريبي للاختبار - تم إنشاؤه تلقائياً	2025-07-07 22:52:04.093075	2025-07-07 22:52:04.093079	https://example.com/delivery	https://example.com/pickup	in_progress
38	23	2025-07-07	\N	maintenance	اختبار تجريبي من النظام	in_progress	500	ورشة الاختبار	فني الاختبار	سجل تجريبي للاختبار - تم إنشاؤه تلقائياً	2025-07-07 22:52:05.404449	2025-07-07 22:52:05.404452	https://example.com/delivery	https://example.com/pickup	in_progress
39	23	2025-07-07	\N	maintenance	اختبار تجريبي من النظام	in_progress	500	ورشة الاختبار	فني الاختبار	سجل تجريبي للاختبار - تم إنشاؤه تلقائياً	2025-07-07 22:52:06.777946	2025-07-07 22:52:06.777949	https://example.com/delivery	https://example.com/pickup	in_progress
40	23	2025-07-07	\N	maintenance	اختبار تجريبي من النظام	in_progress	500	ورشة الاختبار	فني الاختبار	سجل تجريبي للاختبار - تم إنشاؤه تلقائياً	2025-07-07 22:52:08.128387	2025-07-07 22:52:08.128389	https://example.com/delivery	https://example.com/pickup	in_progress
41	23	2025-07-07	\N	maintenance	اختبار تجريبي من النظام	in_progress	500	ورشة الاختبار	فني الاختبار	سجل تجريبي للاختبار - تم إنشاؤه تلقائياً	2025-07-07 22:52:10.063521	2025-07-07 22:52:10.063523	https://example.com/delivery	https://example.com/pickup	in_progress
44	23	2025-07-07	2025-07-08	maintenance	اتماما	completed	0	امان السريع	وىكنتكنت	نامنامنا	2025-07-07 22:53:40.224061	2025-07-07 22:53:40.224064	https://d72f2aef-918c-4148-9723-15870f8c7cf6-00-2c1ygyxvqoldk.riker.replit.dev/mobile/employees	https://d72f2aef-918c-4148-9723-15870f8c7cf6-00-2c1ygyxvqoldk.riker.replit.dev/mobile/employees	in_progress
\.


--
-- Data for Name: vehicle_workshop_image; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicle_workshop_image (id, workshop_record_id, image_type, image_path, uploaded_at, notes) FROM stdin;
1	3	before	uploads/workshop/e7d101c1-ccce-4ab8-a78e-7a8c8a83b3b0_WhatsApp_Image_2025-04-23_at_19.22.36_b28970ea.jpg	2025-04-23 16:23:15.71968	\N
3	9	before	uploads/workshop/07939fd1-7981-4f95-9b5c-79c1beb78f42_WhatsApp_Image_2025-05-11_at_15.10.35_ba9487e0.jpg	2025-05-12 12:58:26.232931	\N
4	25	before	uploads/workshop/6d242a00-bb8c-4297-8f1b-07be3fcddf86_WhatsApp_Image_2025-06-23_at_15.24.04_b45e50f1.jpg	2025-06-23 12:31:40.761066	\N
5	13	after	uploads/workshop/5352e791-97c2-4ce7-b5bf-79c3ca15977e_WhatsApp_Image_2025-06-23_at_15.34.49_5f2a66ee.jpg	2025-06-23 12:36:41.563628	\N
6	26	before	uploads/workshop/0f01e719-f36b-4ffd-9775-8709a98e4119_WhatsApp_Image_2025-06-23_at_15.23.21_f5b4f089.jpg	2025-06-28 10:40:57.787219	\N
7	26	after	uploads/workshop/8066ced9-a5d6-478e-af9f-a2fd73f33bb4_WhatsApp_Image_2025-06-28_at_13.29.10_dfba7b78.jpg	2025-06-28 10:40:57.787224	\N
8	27	before	uploads/workshop/cedc59d5-2d97-4e06-a171-98e2076ab7dc_WhatsApp_Image_2025-06-30_at_22.16.53_29eed474.jpg	2025-06-30 19:58:02.581316	\N
9	28	before	uploads/workshop/1e01d885-89c7-4a61-ae5d-ba7ffcda7294_WhatsApp_Image_2025-07-02_at_17.12.43_df114d40.jpg	2025-07-02 14:30:57.40507	\N
10	23	after	uploads/workshop/7644f666-1682-4477-a323-65eab845d058_WhatsApp_Image_2025-07-03_at_16.32.56_7047a745.jpg	2025-07-03 16:50:24.343062	\N
11	29	before	uploads/workshop/7d57af7a-bbb1-4706-81f3-580577bf4704_WhatsApp_Image_2025-07-05_at_16.32.14_de438bd9.jpg	2025-07-05 13:44:56.761222	\N
12	30	before	uploads/workshop/4fe7d33c-5ec9-4063-8ba9-2bd448dc0be6_WhatsApp_Image_2025-07-06_at_12.06.12_c71abcb8.jpg	2025-07-06 09:13:10.373509	\N
13	30	after	uploads/workshop/71ab6d58-bcd2-49e4-856b-078980b535eb_WhatsApp_Image_2025-07-06_at_12.09.22_a5e9e4ab.jpg	2025-07-06 09:13:10.373513	\N
14	44	before	uploads/workshop/65c7c174-122e-4a34-acfa-c5dd09a363c3_WhatsApp_Image_2025-07-06_at_18.57.35_a014f68a.jpg	2025-07-07 22:53:40.32074	صورة قبل الإصلاح
15	44	after	uploads/workshop/b48f8c96-49b2-448a-b6a0-a13193958912_WhatsApp_Image_2025-07-06_at_18.57.35_a014f68a.jpg	2025-07-07 22:53:40.320744	صورة بعد الإصلاح
\.


--
-- Data for Name: vehicles; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vehicles (id, plate_number, make, model, year, color, status, created_at, updated_at) FROM stdin;
1	أ ب ج 123	تويوتا	كامري	2020	أبيض	active	2025-06-09 17:14:44.299922	2025-06-09 17:14:44.299922
2	د هـ و 456	نيسان	التيما	2019	أزرق	active	2025-06-09 17:14:44.299922	2025-06-09 17:14:44.299922
3	ز ح ط 789	هونداي	النترا	2021	أسود	active	2025-06-09 17:14:44.299922	2025-06-09 17:14:44.299922
\.


--
-- Name: attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.attendance_id_seq', 7797, true);


--
-- Name: audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.audit_log_id_seq', 90, true);


--
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.companies_id_seq', 4, true);


--
-- Name: company_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.company_permissions_id_seq', 1, false);


--
-- Name: company_subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.company_subscriptions_id_seq', 4, true);


--
-- Name: department_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.department_id_seq', 7, true);


--
-- Name: document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.document_id_seq', 76, true);


--
-- Name: employee_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.employee_id_seq', 232, true);


--
-- Name: external_authorization_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.external_authorization_id_seq', 10, true);


--
-- Name: external_authorizations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.external_authorizations_id_seq', 1, false);


--
-- Name: fee_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.fee_id_seq', 1, false);


--
-- Name: fees_cost_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.fees_cost_id_seq', 3, true);


--
-- Name: government_fee_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.government_fee_id_seq', 1, false);


--
-- Name: nationalities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.nationalities_id_seq', 50, true);


--
-- Name: project_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.project_id_seq', 5, true);


--
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.projects_id_seq', 1, false);


--
-- Name: renewal_fee_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.renewal_fee_id_seq', 1, true);


--
-- Name: salary_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.salary_id_seq', 120, true);


--
-- Name: subscription_notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.subscription_notifications_id_seq', 1, false);


--
-- Name: system_audit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.system_audit_id_seq', 1638, true);


--
-- Name: user_department_access_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.user_department_access_id_seq', 21, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.user_id_seq', 12, true);


--
-- Name: user_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.user_permission_id_seq', 53, true);


--
-- Name: vehicle_accident_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_accident_id_seq', 6, true);


--
-- Name: vehicle_checklist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_checklist_id_seq', 4, true);


--
-- Name: vehicle_checklist_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_checklist_image_id_seq', 8, true);


--
-- Name: vehicle_checklist_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_checklist_item_id_seq', 39, true);


--
-- Name: vehicle_damage_marker_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_damage_marker_id_seq', 1, false);


--
-- Name: vehicle_fuel_consumption_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_fuel_consumption_id_seq', 1, true);


--
-- Name: vehicle_handover_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_handover_id_seq', 28, true);


--
-- Name: vehicle_handover_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_handover_image_id_seq', 244, true);


--
-- Name: vehicle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_id_seq', 25, true);


--
-- Name: vehicle_maintenance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_maintenance_id_seq', 4, true);


--
-- Name: vehicle_maintenance_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_maintenance_image_id_seq', 1, false);


--
-- Name: vehicle_periodic_inspection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_periodic_inspection_id_seq', 5, true);


--
-- Name: vehicle_project_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_project_id_seq', 4, true);


--
-- Name: vehicle_rental_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_rental_id_seq', 2, true);


--
-- Name: vehicle_safety_check_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_safety_check_id_seq', 8, true);


--
-- Name: vehicle_workshop_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_workshop_id_seq', 44, true);


--
-- Name: vehicle_workshop_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicle_workshop_image_id_seq', 15, true);


--
-- Name: vehicles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.vehicles_id_seq', 3, true);


--
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: company_permissions company_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.company_permissions
    ADD CONSTRAINT company_permissions_pkey PRIMARY KEY (id);


--
-- Name: company_subscriptions company_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.company_subscriptions
    ADD CONSTRAINT company_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: department department_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_pkey PRIMARY KEY (id);


--
-- Name: document document_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.document
    ADD CONSTRAINT document_pkey PRIMARY KEY (id);


--
-- Name: employee_departments employee_departments_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.employee_departments
    ADD CONSTRAINT employee_departments_pkey PRIMARY KEY (employee_id, department_id);


--
-- Name: employee employee_employee_id_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_employee_id_key UNIQUE (employee_id);


--
-- Name: employee employee_national_id_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_national_id_key UNIQUE (national_id);


--
-- Name: employee employee_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pkey PRIMARY KEY (id);


--
-- Name: external_authorization external_authorization_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.external_authorization
    ADD CONSTRAINT external_authorization_pkey PRIMARY KEY (id);


--
-- Name: external_authorizations external_authorizations_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.external_authorizations
    ADD CONSTRAINT external_authorizations_pkey PRIMARY KEY (id);


--
-- Name: fee fee_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.fee
    ADD CONSTRAINT fee_pkey PRIMARY KEY (id);


--
-- Name: fees_cost fees_cost_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.fees_cost
    ADD CONSTRAINT fees_cost_pkey PRIMARY KEY (id);


--
-- Name: government_fee government_fee_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.government_fee
    ADD CONSTRAINT government_fee_pkey PRIMARY KEY (id);


--
-- Name: nationalities nationalities_name_ar_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.nationalities
    ADD CONSTRAINT nationalities_name_ar_key UNIQUE (name_ar);


--
-- Name: nationalities nationalities_name_en_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.nationalities
    ADD CONSTRAINT nationalities_name_en_key UNIQUE (name_en);


--
-- Name: nationalities nationalities_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.nationalities
    ADD CONSTRAINT nationalities_pkey PRIMARY KEY (id);


--
-- Name: project project_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_pkey PRIMARY KEY (id);


--
-- Name: projects projects_name_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_name_key UNIQUE (name);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: renewal_fee renewal_fee_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.renewal_fee
    ADD CONSTRAINT renewal_fee_pkey PRIMARY KEY (id);


--
-- Name: salary salary_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.salary
    ADD CONSTRAINT salary_pkey PRIMARY KEY (id);


--
-- Name: subscription_notifications subscription_notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.subscription_notifications
    ADD CONSTRAINT subscription_notifications_pkey PRIMARY KEY (id);


--
-- Name: system_audit system_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.system_audit
    ADD CONSTRAINT system_audit_pkey PRIMARY KEY (id);


--
-- Name: user_accessible_departments user_accessible_departments_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_accessible_departments
    ADD CONSTRAINT user_accessible_departments_pkey PRIMARY KEY (user_id, department_id);


--
-- Name: user_department_access user_department_access_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_department_access
    ADD CONSTRAINT user_department_access_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_firebase_uid_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_firebase_uid_key UNIQUE (firebase_uid);


--
-- Name: user_permission user_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_permission
    ADD CONSTRAINT user_permission_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: vehicle_accident vehicle_accident_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_accident
    ADD CONSTRAINT vehicle_accident_pkey PRIMARY KEY (id);


--
-- Name: vehicle_checklist_image vehicle_checklist_image_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_checklist_image
    ADD CONSTRAINT vehicle_checklist_image_pkey PRIMARY KEY (id);


--
-- Name: vehicle_checklist_item vehicle_checklist_item_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_checklist_item
    ADD CONSTRAINT vehicle_checklist_item_pkey PRIMARY KEY (id);


--
-- Name: vehicle_checklist vehicle_checklist_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_checklist
    ADD CONSTRAINT vehicle_checklist_pkey PRIMARY KEY (id);


--
-- Name: vehicle_damage_marker vehicle_damage_marker_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_damage_marker
    ADD CONSTRAINT vehicle_damage_marker_pkey PRIMARY KEY (id);


--
-- Name: vehicle_fuel_consumption vehicle_fuel_consumption_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_fuel_consumption
    ADD CONSTRAINT vehicle_fuel_consumption_pkey PRIMARY KEY (id);


--
-- Name: vehicle_handover_image vehicle_handover_image_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_handover_image
    ADD CONSTRAINT vehicle_handover_image_pkey PRIMARY KEY (id);


--
-- Name: vehicle_handover vehicle_handover_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_handover
    ADD CONSTRAINT vehicle_handover_pkey PRIMARY KEY (id);


--
-- Name: vehicle_maintenance_image vehicle_maintenance_image_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_maintenance_image
    ADD CONSTRAINT vehicle_maintenance_image_pkey PRIMARY KEY (id);


--
-- Name: vehicle_maintenance vehicle_maintenance_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_maintenance
    ADD CONSTRAINT vehicle_maintenance_pkey PRIMARY KEY (id);


--
-- Name: vehicle_periodic_inspection vehicle_periodic_inspection_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_periodic_inspection
    ADD CONSTRAINT vehicle_periodic_inspection_pkey PRIMARY KEY (id);


--
-- Name: vehicle vehicle_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_pkey PRIMARY KEY (id);


--
-- Name: vehicle vehicle_plate_number_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_plate_number_key UNIQUE (plate_number);


--
-- Name: vehicle_project vehicle_project_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_project
    ADD CONSTRAINT vehicle_project_pkey PRIMARY KEY (id);


--
-- Name: vehicle_rental vehicle_rental_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_rental
    ADD CONSTRAINT vehicle_rental_pkey PRIMARY KEY (id);


--
-- Name: vehicle_safety_check vehicle_safety_check_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_safety_check
    ADD CONSTRAINT vehicle_safety_check_pkey PRIMARY KEY (id);


--
-- Name: vehicle_workshop_image vehicle_workshop_image_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_workshop_image
    ADD CONSTRAINT vehicle_workshop_image_pkey PRIMARY KEY (id);


--
-- Name: vehicle_workshop vehicle_workshop_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_workshop
    ADD CONSTRAINT vehicle_workshop_pkey PRIMARY KEY (id);


--
-- Name: vehicles vehicles_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_pkey PRIMARY KEY (id);


--
-- Name: idx_vehicle_make; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_vehicle_make ON public.vehicle USING btree (make);


--
-- Name: idx_vehicle_plate; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_vehicle_plate ON public.vehicle USING btree (plate_number);


--
-- Name: idx_vehicle_project_is_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_vehicle_project_is_active ON public.vehicle_project USING btree (is_active);


--
-- Name: idx_vehicle_project_vehicle_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_vehicle_project_vehicle_id ON public.vehicle_project USING btree (vehicle_id);


--
-- Name: idx_vehicle_rental_is_active; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_vehicle_rental_is_active ON public.vehicle_rental USING btree (is_active);


--
-- Name: idx_vehicle_rental_vehicle_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_vehicle_rental_vehicle_id ON public.vehicle_rental USING btree (vehicle_id);


--
-- Name: idx_vehicle_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_vehicle_status ON public.vehicle USING btree (status);


--
-- Name: idx_vehicle_workshop_entry_date; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_vehicle_workshop_entry_date ON public.vehicle_workshop USING btree (entry_date);


--
-- Name: idx_vehicle_workshop_reason; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_vehicle_workshop_reason ON public.vehicle_workshop USING btree (reason);


--
-- Name: idx_vehicle_workshop_vehicle_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_vehicle_workshop_vehicle_id ON public.vehicle_workshop USING btree (vehicle_id);


--
-- Name: attendance attendance_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: attendance attendance_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id) ON DELETE CASCADE;


--
-- Name: audit_log audit_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: company_permissions company_permissions_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.company_permissions
    ADD CONSTRAINT company_permissions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: company_subscriptions company_subscriptions_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.company_subscriptions
    ADD CONSTRAINT company_subscriptions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: department department_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: department department_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.employee(id) ON DELETE SET NULL;


--
-- Name: document document_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.document
    ADD CONSTRAINT document_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id) ON DELETE CASCADE;


--
-- Name: employee employee_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: employee employee_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id) ON DELETE SET NULL;


--
-- Name: employee_departments employee_departments_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.employee_departments
    ADD CONSTRAINT employee_departments_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id) ON DELETE CASCADE;


--
-- Name: employee_departments employee_departments_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.employee_departments
    ADD CONSTRAINT employee_departments_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id) ON DELETE CASCADE;


--
-- Name: external_authorization external_authorization_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.external_authorization
    ADD CONSTRAINT external_authorization_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id);


--
-- Name: external_authorization external_authorization_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.external_authorization
    ADD CONSTRAINT external_authorization_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.project(id);


--
-- Name: external_authorization external_authorization_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.external_authorization
    ADD CONSTRAINT external_authorization_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id);


--
-- Name: external_authorizations external_authorizations_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.external_authorizations
    ADD CONSTRAINT external_authorizations_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public."user"(id) ON DELETE SET NULL;


--
-- Name: external_authorizations external_authorizations_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.external_authorizations
    ADD CONSTRAINT external_authorizations_created_by_fkey FOREIGN KEY (created_by) REFERENCES public."user"(id) ON DELETE SET NULL;


--
-- Name: external_authorizations external_authorizations_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.external_authorizations
    ADD CONSTRAINT external_authorizations_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: fee fee_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.fee
    ADD CONSTRAINT fee_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.document(id) ON DELETE SET NULL;


--
-- Name: fee fee_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.fee
    ADD CONSTRAINT fee_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id) ON DELETE SET NULL;


--
-- Name: fee fee_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.fee
    ADD CONSTRAINT fee_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE SET NULL;


--
-- Name: fees_cost fees_cost_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.fees_cost
    ADD CONSTRAINT fees_cost_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.document(id) ON DELETE CASCADE;


--
-- Name: government_fee government_fee_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.government_fee
    ADD CONSTRAINT government_fee_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.document(id) ON DELETE SET NULL;


--
-- Name: government_fee government_fee_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.government_fee
    ADD CONSTRAINT government_fee_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id) ON DELETE CASCADE;


--
-- Name: projects projects_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.employee(id) ON DELETE SET NULL;


--
-- Name: renewal_fee renewal_fee_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.renewal_fee
    ADD CONSTRAINT renewal_fee_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.document(id) ON DELETE CASCADE;


--
-- Name: salary salary_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.salary
    ADD CONSTRAINT salary_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: salary salary_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.salary
    ADD CONSTRAINT salary_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id) ON DELETE CASCADE;


--
-- Name: subscription_notifications subscription_notifications_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.subscription_notifications
    ADD CONSTRAINT subscription_notifications_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: system_audit system_audit_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.system_audit
    ADD CONSTRAINT system_audit_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: user_accessible_departments user_accessible_departments_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_accessible_departments
    ADD CONSTRAINT user_accessible_departments_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id) ON DELETE CASCADE;


--
-- Name: user_accessible_departments user_accessible_departments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_accessible_departments
    ADD CONSTRAINT user_accessible_departments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: user user_assigned_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_assigned_department_id_fkey FOREIGN KEY (assigned_department_id) REFERENCES public.department(id);


--
-- Name: user user_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: user user_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_created_by_fkey FOREIGN KEY (created_by) REFERENCES public."user"(id);


--
-- Name: user_department_access user_department_access_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_department_access
    ADD CONSTRAINT user_department_access_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id) ON DELETE CASCADE;


--
-- Name: user_department_access user_department_access_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_department_access
    ADD CONSTRAINT user_department_access_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: user user_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id);


--
-- Name: user user_parent_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_parent_user_id_fkey FOREIGN KEY (parent_user_id) REFERENCES public."user"(id);


--
-- Name: user_permission user_permission_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_permission
    ADD CONSTRAINT user_permission_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: vehicle_accident vehicle_accident_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_accident
    ADD CONSTRAINT vehicle_accident_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: vehicle_checklist_image vehicle_checklist_image_checklist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_checklist_image
    ADD CONSTRAINT vehicle_checklist_image_checklist_id_fkey FOREIGN KEY (checklist_id) REFERENCES public.vehicle_checklist(id) ON DELETE CASCADE;


--
-- Name: vehicle_checklist_item vehicle_checklist_item_checklist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_checklist_item
    ADD CONSTRAINT vehicle_checklist_item_checklist_id_fkey FOREIGN KEY (checklist_id) REFERENCES public.vehicle_checklist(id) ON DELETE CASCADE;


--
-- Name: vehicle_checklist vehicle_checklist_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_checklist
    ADD CONSTRAINT vehicle_checklist_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: vehicle vehicle_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: vehicle_damage_marker vehicle_damage_marker_checklist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_damage_marker
    ADD CONSTRAINT vehicle_damage_marker_checklist_id_fkey FOREIGN KEY (checklist_id) REFERENCES public.vehicle_checklist(id) ON DELETE CASCADE;


--
-- Name: vehicle_fuel_consumption vehicle_fuel_consumption_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_fuel_consumption
    ADD CONSTRAINT vehicle_fuel_consumption_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: vehicle_handover vehicle_handover_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_handover
    ADD CONSTRAINT vehicle_handover_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id);


--
-- Name: vehicle_handover vehicle_handover_supervisor_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_handover
    ADD CONSTRAINT vehicle_handover_supervisor_employee_id_fkey FOREIGN KEY (supervisor_employee_id) REFERENCES public.employee(id);


--
-- Name: vehicle_handover vehicle_handover_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_handover
    ADD CONSTRAINT vehicle_handover_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: vehicle_maintenance_image vehicle_maintenance_image_maintenance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_maintenance_image
    ADD CONSTRAINT vehicle_maintenance_image_maintenance_id_fkey FOREIGN KEY (maintenance_id) REFERENCES public.vehicle_maintenance(id) ON DELETE CASCADE;


--
-- Name: vehicle_maintenance vehicle_maintenance_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_maintenance
    ADD CONSTRAINT vehicle_maintenance_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: vehicle_periodic_inspection vehicle_periodic_inspection_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_periodic_inspection
    ADD CONSTRAINT vehicle_periodic_inspection_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: vehicle_project vehicle_project_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_project
    ADD CONSTRAINT vehicle_project_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: vehicle_rental vehicle_rental_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_rental
    ADD CONSTRAINT vehicle_rental_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: vehicle_rental vehicle_rental_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_rental
    ADD CONSTRAINT vehicle_rental_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: vehicle_safety_check vehicle_safety_check_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_safety_check
    ADD CONSTRAINT vehicle_safety_check_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.employee(id);


--
-- Name: vehicle_safety_check vehicle_safety_check_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_safety_check
    ADD CONSTRAINT vehicle_safety_check_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.employee(id);


--
-- Name: vehicle_safety_check vehicle_safety_check_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_safety_check
    ADD CONSTRAINT vehicle_safety_check_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: vehicle_workshop_image vehicle_workshop_image_workshop_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_workshop_image
    ADD CONSTRAINT vehicle_workshop_image_workshop_record_id_fkey FOREIGN KEY (workshop_record_id) REFERENCES public.vehicle_workshop(id) ON DELETE CASCADE;


--
-- Name: vehicle_workshop vehicle_workshop_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vehicle_workshop
    ADD CONSTRAINT vehicle_workshop_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE CASCADE;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

