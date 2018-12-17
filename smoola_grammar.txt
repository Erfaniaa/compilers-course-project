grammar Smoola;

    @header{
        import ast.*;
        import ast.node.*;
        import ast.node.declaration.*;
        import ast.node.expression.*;
        import ast.node.expression.Value.*;
        import ast.node.statement.*;
        import ast.Type.*;
        import ast.Type.ArrayType.*;
        import ast.Type.PrimitiveType.*;
        import ast.Type.UserDefinedType.*;
    }

    program returns [Program prog]:
        {
            $prog = new Program();
        }
        main = mainClass { $prog.setMainClass($main.mainClassDec); }
        (classDec = classDeclaration { $prog.addClass($classDec.classDec); } )* EOF
    ;

    mainClass returns [ClassDeclaration mainClassDec]:
        // name should be checked later
        'class' className = ID {
            Identifier identifier1 = new Identifier($className.text);
            identifier1.setLine($className.getLine());
            $mainClassDec = new ClassDeclaration(identifier1, null);
            $mainClassDec.setLine($className.getLine());
        }
        '{' 'def' methodName = ID '(' ')' ':' 'int' '{'  stmnts = statements 'return' returnExpr = expression ';' '}' '}'
        {
            Identifier identifier2 = new Identifier($methodName.text);
            identifier2.setLine($methodName.getLine());
            MethodDeclaration methodDec = new MethodDeclaration(identifier2);
            methodDec.setLine($methodName.getLine());
            for (Statement stmnt : $stmnts.stmnts)
                methodDec.addStatement(stmnt);
            methodDec.setReturnType(new IntType());
            methodDec.setReturnValue($returnExpr.expr);
            $mainClassDec.addMethodDeclaration(methodDec);
        }
    ;

    classDeclaration returns [ClassDeclaration classDec]:
        'class' className = ID ('extends' parentName = ID)?
        {
            Identifier classId = new Identifier($className.text);
            classId.setLine($className.getLine());
            Identifier parentId = new Identifier($parentName.text);
            if ($parentName != null) {
                parentId.setLine($parentName.getLine());
            }
            $classDec = new ClassDeclaration(classId, parentId);
            $classDec.setLine($className.getLine());
        }
        '{' (varDec = varDeclaration { $classDec.addVarDeclaration($varDec.varDec); } )*
        (methodDec = methodDeclaration { $classDec.addMethodDeclaration($methodDec.methodDec); } )* '}'
    ;

    varDeclaration returns [VarDeclaration varDec]:
        'var' name = ID ':' varType = type ';'
        {
            Identifier identifier = new Identifier($name.text);
            identifier.setLine($name.getLine());
            $varDec = new VarDeclaration(identifier, $varType.synType);
            $varDec.setLine($name.getLine());
        }
    ;

    methodDeclaration returns [MethodDeclaration methodDec]:
        'def' name = ID {
            Identifier methodId = new Identifier($name.text);
            methodId.setLine($name.getLine());
            $methodDec = new MethodDeclaration(methodId);
            $methodDec.setLine($name.getLine());
        }
        ('(' ')'
        | ('(' argName1 = ID ':' argType1 = type {
            Identifier argId1 = new Identifier($argName1.text);
            argId1.setLine($argName1.getLine());
            VarDeclaration var1 = new VarDeclaration(argId1, $argType1.synType);
            var1.setLine($argName1.getLine());
            $methodDec.addArg(var1);
        }
        (',' argName2 = ID ':' argType2 = type {
            Identifier argId2 = new Identifier($argName2.text);
            argId2.setLine($argName2.getLine());
            VarDeclaration var2 = new VarDeclaration(argId2, $argType2.synType);
            var2.setLine($argName2.getLine());
            $methodDec.addArg(var2);
        })* ')'))
        ':' returnType = type { $methodDec.setReturnType($returnType.synType); }
        '{' (varDec = varDeclaration { $methodDec.addLocalVar($varDec.varDec); })*
        stmnts = statements {
            for (Statement stmnt : $stmnts.stmnts)
                $methodDec.addStatement(stmnt);
        }
        'return' returnValue = expression ';' '}' { $methodDec.setReturnValue($returnValue.expr); }
    ;

    statements returns [ArrayList<Statement> stmnts]:
        {
            $stmnts = new ArrayList<>();
        }
        (stmnt = statement { $stmnts.add($stmnt.stmnt); } )*
    ;

    statement returns [Statement stmnt]:
        {
            $stmnt = new Statement();
        }
        block = statementBlock { $stmnt = $block.block; } |
        cond = statementCondition { $stmnt = $cond.cond; } |
        loop = statementLoop { $stmnt = $loop.loop; } |
        write = statementWrite { $stmnt = $write.write; } |
        assign = statementAssignment { $stmnt = $assign.assign; }
    ;

    statementBlock returns [Block block]:
        '{' stmnts = statements '}'
        {
            $block = new Block();
            for (Statement stmnt : $stmnts.stmnts)
                $block.addStatement(stmnt);
        }
    ;

    statementCondition returns [Conditional cond]:
        'if' id = '(' expr = expression ')' 'then' cons = statement
        {
            $cond = new Conditional($expr.expr, $cons.stmnt);
            $cond.setLine($id.getLine());
        }
        ('else' alt = statement { $cond.setAlternativeBody($alt.stmnt); } )?
    ;

    statementLoop returns [While loop]:
        'while' id = '(' condExpr = expression ')' body = statement
        {
            $loop = new While($condExpr.expr, $body.stmnt);
            $loop.setLine($id.getLine());
        }
    ;

    statementWrite returns [Write write]:
        id = 'writeln(' arg = expression ')' ';'
        {
            $write = new Write($arg.expr);
            $write.setLine($id.getLine());
        }
    ;

    statementAssignment returns [Assign assign]:
        expr = expression id = ';'
        {
            if ($expr.assignExpr != null) {
                $assign = new Assign($expr.assignExpr.getLeft(), $expr.assignExpr.getRight());
            } else {
                $assign = new Assign(null, null);
            }
            $assign.setLine($id.getLine());
        }
    ;

    expression returns [Expression expr, BinaryExpression assignExpr]:
		expr1 = expressionAssignment
		{
    	    $expr = $expr1.expr;
    	    $assignExpr = $expr1.assignExpr;
		}
	;

    expressionAssignment returns [Expression expr, BinaryExpression assignExpr]:
		leftExpr = expressionOr id = '=' rightExpr = expressionAssignment
		{
		    $assignExpr = new BinaryExpression($leftExpr.expr, $rightExpr.expr, BinaryOperator.assign);
		    $expr = $assignExpr;
		    $expr.setLine($id.getLine());
		}
	    |	expr1 = expressionOr
	    {
	        $expr = $expr1.expr;
	    }
	;

    expressionOr returns [Expression expr]:
		andExpr = expressionAnd orTempExpr = expressionOrTemp
		{
		    if ($orTempExpr.expr == null) {
		        $expr = $andExpr.expr;
		    } else {
		        $expr = new BinaryExpression($andExpr.expr, $orTempExpr.expr, BinaryOperator.or);
		        $expr.setLine($andExpr.expr.getLine());
		    }
		}
	;

    expressionOrTemp returns [Expression expr]:
		id = '||' andExpr = expressionAnd orTempExpr = expressionOrTemp
		{
		    if ($orTempExpr.expr == null) {
		        $expr = $andExpr.expr;
		    } else {
		        $expr = new BinaryExpression($andExpr.expr, $orTempExpr.expr, BinaryOperator.or);
		        $expr.setLine($id.getLine());
		    }
		}
	    |
	    {
	        $expr = null;
	    }
	;

    expressionAnd returns [Expression expr]:
		eqExpr = expressionEq andTempExpr = expressionAndTemp
		{
		    if ($andTempExpr.expr == null) {
		        $expr = $eqExpr.expr;
		    } else {
		        $expr = new BinaryExpression($eqExpr.expr, $andTempExpr.expr, BinaryOperator.and);
		        $expr.setLine($eqExpr.expr.getLine());
		    }
		}
	;

    expressionAndTemp returns [Expression expr]:
		id = '&&' eqExpr = expressionEq andTempExpr = expressionAndTemp
		{
		    if ($andTempExpr.expr == null) {
		        $expr = $eqExpr.expr;
		    } else {
		        $expr = new BinaryExpression($eqExpr.expr, $andTempExpr.expr, BinaryOperator.and);
		        $expr.setLine($id.getLine());
		    }
		}
	    |
	    {
	        $expr = null;
	    }
	;

    expressionEq returns [Expression expr]:
		cmpExpr = expressionCmp eqTempExpr = expressionEqTemp
		{
		    if ($eqTempExpr.expr == null) {
		        $expr = $cmpExpr.expr;
		    } else {
		        $expr = new BinaryExpression($cmpExpr.expr, $eqTempExpr.expr, $eqTempExpr.synOp);
		        $expr.setLine($cmpExpr.expr.getLine());
		    }
		}
	;

    expressionEqTemp returns [Expression expr, BinaryOperator synOp]:
		op = ('==' | '<>') cmpExpr = expressionCmp eqTempExpr = expressionEqTemp
		{
		    if ($op.text.equals("<>"))
		        $synOp = BinaryOperator.neq;
            else
                $synOp = BinaryOperator.eq;
		    if ($eqTempExpr.expr == null) {
		        $expr = $cmpExpr.expr;
		    } else {
		        $expr = new BinaryExpression($cmpExpr.expr, $eqTempExpr.expr, $eqTempExpr.synOp);
		        $expr.setLine($op.getLine());
		    }
		}
	    |
	    {
	        $expr = null;
	        $synOp = null;
	    }
	;

    expressionCmp returns [Expression expr]:
		addExpr = expressionAdd cmpTempExpr = expressionCmpTemp
		{
		    if ($cmpTempExpr.expr == null) {
		        $expr = $addExpr.expr;
		    } else {
		        $expr = new BinaryExpression($addExpr.expr, $cmpTempExpr.expr, $cmpTempExpr.synOp);
		        $expr.setLine($addExpr.expr.getLine());
		    }
		}
	;

    expressionCmpTemp returns [Expression expr, BinaryOperator synOp]:
		op = ('<' | '>') addExpr = expressionAdd cmpTempExpr = expressionCmpTemp
		{
			if ($op.text.equals("<"))
			    $synOp = BinaryOperator.lt;
			else
			    $synOp = BinaryOperator.gt;
		    if ($cmpTempExpr.expr == null) {
		        $expr = $addExpr.expr;
		    } else {
		        $expr = new BinaryExpression($addExpr.expr, $cmpTempExpr.expr, $cmpTempExpr.synOp);
		        $expr.setLine($op.getLine());
		    }
		}
	    |
	    {
	        $expr = null;
	        $synOp = null;
	    }
	;

    expressionAdd returns [Expression expr]:
		mulExpr = expressionMult addTempExpr = expressionAddTemp
		{
		    if ($addTempExpr.expr == null) {
		        $expr = $mulExpr.expr;
		    } else {
		        $expr = new BinaryExpression($mulExpr.expr, $addTempExpr.expr, $addTempExpr.synOp);
		        $expr.setLine($mulExpr.expr.getLine());
		    }
		}
	;

    expressionAddTemp returns [Expression expr, BinaryOperator synOp]:
		op = ('+' | '-') mulExpr = expressionMult addTempExpr = expressionAddTemp
		{
		    if ($op.text.equals("+"))
		        $synOp = BinaryOperator.add;
            else
                $synOp = BinaryOperator.sub;
		    if ($addTempExpr.expr == null) {
		        $expr = $mulExpr.expr;
		    } else {
		        $expr = new BinaryExpression($mulExpr.expr, $addTempExpr.expr, $addTempExpr.synOp);
		        $expr.setLine($op.getLine());
		    }
		}
	    |
	    {
	        $expr = null;
	        $synOp = null;
	    }
	;

    expressionMult returns [Expression expr]:
		unaryExpr = expressionUnary mulTempExpr = expressionMultTemp
		{
		    if ($mulTempExpr.expr == null) {
		        $expr = $unaryExpr.expr;
		    } else {
		        $expr = new BinaryExpression($unaryExpr.expr, $mulTempExpr.expr, $mulTempExpr.synOp);
		        $expr.setLine($unaryExpr.expr.getLine());
		    }
		}
	;

    expressionMultTemp returns [Expression expr, BinaryOperator synOp]:
		op = ('*' | '/') unaryExpr = expressionUnary mulTempExpr = expressionMultTemp
		{
		    if ($op.text.equals("*"))
		        $synOp = BinaryOperator.mult;
		    else
		        $synOp = BinaryOperator.div;
		    if ($mulTempExpr.expr == null) {
		        $expr = $unaryExpr.expr;
		    } else {
		        $expr = new BinaryExpression($unaryExpr.expr, $mulTempExpr.expr, $mulTempExpr.synOp);
		        $expr.setLine($op.getLine());
		    }
		}
	    |
	    {
	        $expr = null;
	        $synOp = null;
	    }
	;

    expressionUnary returns [Expression expr]:
		op = ('!' | '-') unaryExpr = expressionUnary
		{
		    UnaryOperator unaryOp;
		    if ($op.text.equals("!"))
		        unaryOp = UnaryOperator.not;
		    else
		        unaryOp = UnaryOperator.minus;
		    $expr = new UnaryExpression(unaryOp, $unaryExpr.expr);
		    $expr.setLine($op.getLine());
		}
	    |	memExpr = expressionMem
	    {
	        $expr = $memExpr.expr;
	    }
	;

    expressionMem returns [Expression expr]:
		methodsExpr = expressionMethods memTempExpr = expressionMemTemp
		{
		    if ($memTempExpr.expr == null) {
		        $expr = $methodsExpr.expr;
		    } else {
		        $expr = new ArrayCall($methodsExpr.expr, $memTempExpr.expr);
		        $expr.setLine($methodsExpr.expr.getLine());
		    }
		}
	;

    expressionMemTemp returns [Expression expr]:
		'[' expr1 = expression ']'
		{
		    $expr = $expr1.expr;
		}
	    |
	    {
	        $expr = null;
	    }
	;
	expressionMethods returns [Expression expr]:
	    otherExpr = expressionOther methodsTempExpr = expressionMethodsTemp [$otherExpr.expr]
	    {
	        if ($methodsTempExpr.expr == null) {
	            $expr = $otherExpr.expr;
	        } else{
	            $expr = $methodsTempExpr.expr;
	        }
	    }
	;

	expressionMethodsTemp [Expression inhInstanceName] returns [Expression expr]:
	    '.' (
	        methodName = ID '(' ')' {
	            Identifier methodId = new Identifier($methodName.text);
	            methodId.setLine($methodName.getLine());
	            $expr = new MethodCall($inhInstanceName, methodId);
	            $expr.setLine($inhInstanceName.getLine());
	        }
	        | methodName = ID {
	            Identifier methodTmpId = new Identifier($methodName.text);
	            methodTmpId.setLine($methodName.getLine());
	            MethodCall tmp = new MethodCall($inhInstanceName, methodTmpId);
	            tmp.setLine($inhInstanceName.getLine());
	        }
	        '(' (arg1 = expression { tmp.addArg($arg1.expr); } (',' arg2 = expression { tmp.addArg($arg2.expr); } )*) ')'
	        { $expr = tmp; }
	        | 'length' {
	            $expr = new Length($inhInstanceName);
	            $expr.setLine($inhInstanceName.getLine());
	        }
	    ) expr1 = expressionMethodsTemp [$expr] { $expr = $expr1.expr; }
	    |
	    {
	        $expr = $inhInstanceName;
	    }
	;

    expressionOther returns [Expression expr]:
		num = CONST_NUM {
		    $expr = new IntValue($num.int, new IntType());
		    $expr.setLine($num.getLine());
		}
        |	str = CONST_STR {
            $expr = new StringValue($str.text, new StringType());
            $expr.setLine($str.getLine());
        }
        |   'new ' 'int' '[' size = CONST_NUM ']'
            {
                NewArray tmp = new NewArray();
                Expression value = new IntValue($size.int, new IntType());
                value.setLine($size.getLine());
                tmp.setExpression(value);
                $expr = tmp;
                $expr.setLine($size.getLine());
            }
        |   'new ' className = ID '(' ')' {
            Identifier id = new Identifier($className.text);
            id.setLine($className.getLine());
            $expr = new NewClass(id);
            $expr.setLine($className.getLine());
        }
        |
            name = 'new Object()' {
            $expr = new ObjectValue(new ObjectType());
            $expr.setLine($name.getLine());
        }
        |   name = 'this' {
                $expr = new This();
                $expr.setLine($name.getLine());
            }
        |   name = 'true' {
                $expr = new BooleanValue(true, new BooleanType());
                $expr.setLine($name.getLine());
            }
        |   name = 'false' {
                $expr = new BooleanValue(false, new BooleanType());
                $expr.setLine($name.getLine());
            }
        |	name = ID {
            $expr = new Identifier($name.text);
            $expr.setLine($name.getLine());
        }
        |   name = ID '[' index = expression ']' {
            Identifier id = new Identifier($name.text);
            id.setLine($name.getLine());
            $expr = new ArrayCall(id, $index.expr);
            $expr.setLine($name.getLine());
        }
        |	id = '(' ex = expression ')' { $expr = $ex.expr; $expr.setLine($id.getLine()); }
	;

	type returns [Type synType]:
	    'int'
	    {
	        $synType = new IntType();
        }
        |
	    'boolean'
	    {
	        $synType = new BooleanType();
        }
	    |
	    'string'
	    {
	        $synType = new StringType();
        }
	    |
	    'int' '[' ']'
	    {
	        $synType = new ArrayType();
        }
	    |
	    identifier = ID
	    {
	        UserDefinedType tmp = new UserDefinedType();
	        Identifier id = new Identifier($identifier.text);
	        id.setLine($identifier.getLine());
	        tmp.setName(id);
	        $synType = tmp;
        }
        |
        'Object' {
            $synType = new ObjectType();
        }
	;

    CONST_NUM:
		[0-9]+
	;

    CONST_STR:
		'"' ~('\r' | '\n' | '"')* '"'
	;
    NL:
		'\r'? '\n' -> skip
	;

    ID:
		[a-zA-Z_][a-zA-Z0-9_]*
	;

    COMMENT:
		'#'(~[\r\n])* -> skip
	;

    WS:
    	[ \t] -> skip
    ;