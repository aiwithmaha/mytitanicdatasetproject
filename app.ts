const passengers: number = 2224;
const survivors: number = 710;
function survivalRate(total: number, saved: number): number {
  return (saved / total) * 100;
}
const rate: number = survivalRate(passengers, survivors);
console.log("Titanic survival rate:", rate, "%");
if (rate > 30) {
  console.log("More than 30% survived");
}
