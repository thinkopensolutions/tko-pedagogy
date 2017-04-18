# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Thinkopen Solutions, Lda. All Rights Reserved
#    http://www.thinkopensolutions.com.
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# Inspired by http://lybniz2.sourceforge.net/safeeval.html
import ast


class FormulaNamesExtractor(ast.NodeVisitor):
    def __init__(self):
        self.names = []

    def visit_Name(self, node):
        self.names.append(node.id)

    def visit(self, node):
        super(FormulaNamesExtractor, self).visit(node)
        return self.names


class Formula(object):
    def __init__(self, formula_text):
        self._formula = formula_text
        self.names = FormulaNamesExtractor().visit(ast.parse(formula_text))

    def _build_values_dict(self, values):
        # make a list of safe functions
        safe_list = ['math', 'abs', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'de grees', 'e', 'exp',
                     'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians',
                     'sin', 'sinh', 'sqrt', 'tan', 'tanh']
        # use the list to filter the local namespace
        safe_dict = dict([(k, locals().get(k, None)) for k in safe_list])
        # add factors values
        safe_dict.update(values)
        return safe_dict

    def calculate(self, values):
        valuesDict = self._build_values_dict(values)
        return eval(self._formula, {'__builtins__': None}, valuesDict)


def test():
    formula_text = '(test1 + test2) * 1.25 + paper * 2.5'
    factorValues = {
        'test1': 14.0,
        'test2': 16.0,
        'paper': 12.0
    }

    formula = Formula(formula_text)
    result = formula.calculate(factorValues)
    assert formula.names == ['test1', 'test2', 'paper']
    assert result == 67.5

    formula_text = '(this is not right'
    try:
        formula = Formula(formula_text)
        assert False, 'Shouldn\'t have reached this line'
    except SyntaxError as se:
        pass  # OK
