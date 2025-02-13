export  const findArrItemByValue = (arr: Object[],value: any) => {
  let item = arr.find((item) => Object.values(item)[0] === value);
  return item;
}

export const findArrItemByKey = (arr: Object[],key: any) => {
  let item = arr.find((item) => Object.keys(item)[0] === key);
  return item;
}
