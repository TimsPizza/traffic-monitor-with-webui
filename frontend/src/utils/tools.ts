import { IProtocolDistributionResponseRecord } from "./../client/api/models/response";

export const findArrItemByValue = (arr: Object[], value: any) => {
  let item = arr.find((item) => Object.values(item)[0] === value);
  return item;
};

export const findArrItemByKey = (arr: Object[], key: any) => {
  let item = arr.find((item) => Object.keys(item)[0] === key);
  return item;
};

export const getProtocolDistributionRecordByProtocol = (
  key: string,
  obj: IProtocolDistributionResponseRecord,
) => {
  const dataArr = obj["distribution"];
  for (const item of dataArr) {
    if (item.protocol === key) {
      return item;
    }
  }
  return null;
};

export const bytesToSize = (bytes: number) => {
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  if (bytes === 0) return {
    size: 0,
    unit: sizes[0],
  }
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return {
    size: (bytes / Math.pow(1024, i)).toFixed(1),
    unit: sizes[i],
  }
  
}
