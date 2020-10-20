-- Table: public.ExpressionTasks

-- DROP TABLE public."ExpressionTasks";

CREATE TABLE public."ExpressionTasks"
(
    expression_id bigserial NOT NULL,
    expression character varying(512) COLLATE pg_catalog."default" NOT NULL,
    variables json NOT NULL,
    added_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    process_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "ExpressionTasks_pkey" PRIMARY KEY (expression_id)
)

TABLESPACE pg_default;

-- Index: ExpressionTasks_Cl_IX

-- DROP INDEX public."ExpressionTasks_Cl_IX";

CREATE UNIQUE INDEX "ExpressionTasks_Cl_IX"
    ON public."ExpressionTasks" USING btree
    (expression_id ASC NULLS LAST)
    TABLESPACE pg_default;
ALTER TABLE public."ExpressionTasks"
    CLUSTER ON "ExpressionTasks_Cl_IX";