import sys
from lark import Lark, Transformer, Tree

def map_template_names(items):
    pass

class BaseTransformer(Transformer):
    def int(self, items):
        return "INTEGER"
    def var2(self, items):
        var2par1 = self.get_data("var2par1", items)
        if var2par1:
            return "VARCHAR(" + var2par1 + ")"
        return "VARCHAR"
    def WORD(self, items):
        return str(items)
    def get_data(self, key, items):
        data = next(Tree("", items).find_data(key), None)
        if isinstance(data, Tree):
            data = data.children[0]
        return data

class OracleToPostgresTransformer(BaseTransformer):
    def stmts(self, items):
        return [item for item in items]
    def stmt(self, items):
        return [stmt + ";" for stmt in items[0]]
    def atac(self, items):
        atac = AddColumn().transform(Tree("stmt", items))
        return atac
    def atdc(self, items):
        atdc = DropColumn().transform(Tree("stmt", items))
        return atdc
    def atmc(self, items):
        atmc = ModifyColumn().transform(Tree("stmt", items))
        return atmc

class PlainTransformer(BaseTransformer):
    def altertable(self, items):
        return "alter table"
    def addcolumn(self, items):
        return "add column"
    def dropcolumn(self, items):
        return "drop column"
    def modifycolumn(self, items):
        return "modify column"
    def tablename(self, items):
        return items[0]
    def columnname(self, items):
        return items[0]
    def columntype(self, items):
        return items[0]
    def coldef(self, items):
        return " ".join(items)
    def null(self, items):
        return "NULL"
    def not_null(self, items):
        return "NOT NULL"

class AddColumn(PlainTransformer):
    def stmt(self, items):
        return [" ".join(items)]

class DropColumn(PlainTransformer):
    def stmt(self, items):
        return [" ".join(items)]

class ModifyColumn(BaseTransformer):
    def stmt(self, items):
        columnname = self.get_data("columnname", items)
        tablename = self.get_data("tablename", items)
        has_column_type = self.get_data("columntype", items)
        has_null = self.get_data("null", items)
        has_not_null = self.get_data("not_null", items)
        stmts = []
        if has_column_type:
            stmts += ["alter table " + tablename + " alter column " + columnname + " type " + has_column_type]
        if has_null:
            stmts += ["alter table " + tablename + " alter column " + columnname + " drop not_null"]
        if has_not_null:
            stmts += ["alter table " + tablename + " alter column " + columnname + " set not_null"]
        return stmts
    def null(self, items):
        return Tree("null", ["NULL"])
    def not_null(self, items):
        return Tree("not_null", ["NOT NULL"])

oracle_grammar = Lark('''
         ?stmts: (stmt)*
         stmt: [ atac | atdc | atmc ] ";"
         altertable: "alter table"i
         addcolumn: "add"i "column"i
         dropcolumn: "drop"i "column"i
         int: "INTEGER"i
         var2par1: NUMBER
         var2: "VARCHAR2"i "(" var2par1 ")"
         columntype: int | var2
         modifycolumn: "modify"i "column"i
         null: "NULL"i
         not_null: "NOT NULL"i
         coldef: columnname columntype [ null | not_null ]
         atac: altertable tablename addcolumn coldef
         atdc: altertable tablename dropcolumn columnname
         atmc: altertable tablename modifycolumn coldef
         cr: "create"i "table"i tablename "(" coldef ")"
         tablename: WORD
         columnname: WORD
%import common.NUMBER
%import common.WORD
%import common.WS
%ignore WS
''', start="stmts")

class OracleToPostgresConverter:
    def convert(self, oracle_sql_text):
        parse_tree = oracle_grammar.parse(oracle_sql_text)
        postgres_sql_stmts = OracleToPostgresTransformer().transform(parse_tree)
        postgres_sql_text = "\n".join([stmt for stmt in postgres_sql_stmts])
        return postgres_sql_text

if __name__ == "__main__":
    with open('oracle.sql') as f:
        oracle_sql_text = f.read()

    parse_tree = oracle_grammar.parse(oracle_sql_text)

    postgres_sql_text = OracleToPostgresTransformer().transform(parse_tree)

    for stmts in postgres_sql_text:
        for stmt in stmts:
            print(stmt)
