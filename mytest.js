const ship = "titanic";
const passengers = 2224;
console.log("Ship:", ship, "| Passengers:", passengers);
function survive(total, saved) {
  return (saved / total) * 100;
}
console.log(survive(passengers, 710));

function multiply(a, b) {
  return a * b;
}

console.log(multiply(3, 4));

function divide(a, b) {
  return a / b;
}
console.log(divide(10, 2));

function add(a, b) {
  const result = a + b;
  console.log("result is:" + result);
  return result;
}
add(5, 10);


