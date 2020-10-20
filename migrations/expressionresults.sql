-- Table: public.ExpressionResults

-- DROP TABLE public."ExpressionResults";

CREATE TABLE public."ExpressionResults"
(
    expression_id bigint NOT NULL,
    expression character varying(512) COLLATE pg_catalog."default" NOT NULL,
    variables json NOT NULL,
    result double precision,
    error_code smallint NOT NULL,
    added_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

-- Index: ExpressionResults_Cl_IX

-- DROP INDEX public."ExpressionResults_Cl_IX";

CREATE INDEX "ExpressionResults_Cl_IX"
    ON public."ExpressionResults" USING btree
    (expression_id ASC NULLS LAST)
    TABLESPACE pg_default;

ALTER TABLE public."ExpressionResults"
    CLUSTER ON "ExpressionResults_Cl_IX";