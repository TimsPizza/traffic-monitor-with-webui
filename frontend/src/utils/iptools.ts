export const isIpv4OrCIDR = (ip: string): boolean => {
  return /^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$/.test(ip);
}

export const isIpv6OrCIDR = (ip: string): boolean => {
  return /^([0-9a-fA-F]{1,4}:){7}([0-9a-fA-F]{1,4}|:)$/.test(ip);
}

export const isValidPort = (port: number): boolean => {
  return port >= 0 && port <= 65535;
}