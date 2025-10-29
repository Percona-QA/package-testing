#!/bin/bash
set -e

# Define MySQL command (adjust credentials if needed)
MYSQL="mysql -uroot -NBe"

echo "==== Installing JS Component ===="
$MYSQL "INSTALL COMPONENT 'file://component_js_lang';" || {
    echo "❌ Failed to install JS component"
    exit 1
}

# Verify installation
JS_COMPONENT=$($MYSQL "SELECT COUNT(*) FROM mysql.component WHERE component_urn='file://component_js_lang';")
if [[ "$JS_COMPONENT" -eq 1 ]]; then
    echo "✅ JS component installed successfully"
else
    echo "❌ ERROR: JS component not found after installation"
    exit 1
fi

# Grant permissions for JS routines
echo "==== Granting CREATE_JS_ROUTINE privilege ===="
$MYSQL "GRANT CREATE_JS_ROUTINE ON *.* TO 'root'@'localhost';"
$MYSQL "create database test;"

# Create factorial function
echo "==== Creating JS factorial function ===="
$MYSQL "USE test;
DROP FUNCTION IF EXISTS fact;
CREATE FUNCTION fact(n INT)
RETURNS INT
DETERMINISTIC
NO SQL
LANGUAGE JS
AS \$\$
  let result = 1;
  while (n > 1) {
    result *= n;
    n--;
  }
  return result;
\$\$;"

# Validate function definition in INFORMATION_SCHEMA
echo "==== Verifying function metadata in INFORMATION_SCHEMA ===="
ROUTINE_INFO=$($MYSQL "SELECT routine_schema, routine_name, external_language
                       FROM INFORMATION_SCHEMA.ROUTINES
                       WHERE routine_name='fact';")

if echo "$ROUTINE_INFO" | grep -q "JS"; then
    echo "✅ JS function 'fact' correctly registered in INFORMATION_SCHEMA"
else
    echo "❌ Function metadata missing or incorrect"
    exit 1
fi

# Test the function output
echo "==== Testing factorial function ===="
FACTORIAL_RESULT=$($MYSQL "use test; SELECT fact(5);")
if [[ "$FACTORIAL_RESULT" -eq 120 ]]; then
    echo "✅ fact(5) returned expected result: $FACTORIAL_RESULT"
else
    echo "❌ fact(5) returned unexpected result: $FACTORIAL_RESULT"
    exit 1
fi

# Test multiple values
for i in 0 1 3 7; do
    expected=$(python3 -c "import math; print(math.factorial($i))")
    result=$($MYSQL "use test; SELECT fact($i);")
    if [[ "$result" -eq "$expected" ]]; then
        echo "✅ fact($i) = $result (as expected)"
    else
        echo "❌ fact($i) returned $result instead of $expected"
        exit 1
    fi
done

# Drop the function
echo "==== Dropping factorial function ===="
$MYSQL "use test; DROP FUNCTION IF EXISTS fact;"

# Verify removal from INFORMATION_SCHEMA
echo "==== Verifying function removal ===="
FUNC_COUNT=$($MYSQL "SELECT COUNT(*) FROM INFORMATION_SCHEMA.ROUTINES WHERE routine_name='fact';")
if [[ "$FUNC_COUNT" -eq 0 ]]; then
    echo "✅ Function 'fact' successfully removed"
else
    echo "❌ Function 'fact' still exists after DROP"
    exit 1
fi

# Uninstall the JS component
echo "==== Uninstalling JS Component ===="
$MYSQL "UNINSTALL COMPONENT 'file://component_js_lang';" || {
    echo "❌ Failed to uninstall JS component"
    exit 1
}

# Verify uninstall
JS_COMPONENT_LEFT=$($MYSQL "SELECT COUNT(*) FROM mysql.component WHERE component_urn='file://component_js_lang';")
if [[ "$JS_COMPONENT_LEFT" -eq 0 ]]; then
    echo "✅ JS component uninstalled successfully"
else
    echo "❌ ERROR: JS component still present after uninstall"
    exit 1
fi

echo "🎉 All JS component tests passed successfully!"
