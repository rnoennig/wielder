alter table workflow drop column workflowstepid;
alter table workflow add column workflowstepid INTEGER;
alter table workflow modify column id INTEGER;
alter table portfolio drop column workflowid;
alter table workflow modify column id VARCHAR2(255);
alter table workflow modify column created VARCHAR2(255) NOT NULL;
