import { useState } from 'react';
import { useCardData } from './useProtocolCardData';
import { TimeRange } from '../components/TimeRangeSelector';
import { ApiError } from '../client/api/models/base';

const DEFAULT_PROTOCOLS = ["HTTPS", "HTTP", "SSH", "Unknown"] as const;
export type Protocol = (typeof DEFAULT_PROTOCOLS)[number];
export const AVAILABLE_PROTOCOLS: Protocol[] = ["HTTPS", "HTTP", "SSH", "Unknown"];

const LOCAL_STORAGE_KEY = 'dashboard_protocols';

export interface ProtocolData {
  protocol: Protocol;
  loading: boolean;
  current: {
    value: number;
    label: string;
    secondaryValue?: number;
  };
  trend?: number;
  error?: Error | ApiError;
}

interface UseProtocolsDataOptions {
  timeRange: TimeRange;
  initialProtocols?: Protocol[];
}

// 获取初始协议列表
function getInitialProtocols(): Protocol[] {
  try {
    const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (!saved) return AVAILABLE_PROTOCOLS;
    const protocols = JSON.parse(saved) as Protocol[];
    return protocols.every(p => AVAILABLE_PROTOCOLS.includes(p)) ? protocols : AVAILABLE_PROTOCOLS;
  } catch {
    return AVAILABLE_PROTOCOLS;
  }
}

export function useProtocolsData({ 
  timeRange, 
  initialProtocols = getInitialProtocols()
}: UseProtocolsDataOptions) {
  const [protocols, setProtocols] = useState<Protocol[]>(initialProtocols);

  // 为每个协议创建单独的查询
  const protocolQueries = protocols.map(protocol => ({
    protocol,
    data: useCardData({
      timeRange,
      queryType: 'protocolDistribution',
      compareWithPrevious: true,
      protocol,
    })
  }));

  function saveProtocols(newProtocols: Protocol[]) {
    try {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(newProtocols));
    } catch (error) {
      console.error('Failed to save protocols:', error);
    }
  }

  function addProtocol(protocol: Protocol) {
    if (protocols.includes(protocol)) return;
    const newProtocols = [...protocols, protocol];
    setProtocols(newProtocols);
    saveProtocols(newProtocols);
  }

  function removeProtocol(protocol: Protocol) {
    const newProtocols = protocols.filter(p => p !== protocol);
    setProtocols(newProtocols);
    saveProtocols(newProtocols);
  }

  function resetProtocols() {
    setProtocols(AVAILABLE_PROTOCOLS);
    saveProtocols(AVAILABLE_PROTOCOLS);
  }

  const protocolsData = protocolQueries.map(({ protocol, data }) => ({
    protocol,
    loading: data.isLoading,
    current: data.current || {
      value: 0,
      label: 'B',
    },
    trend: data.trend,
    error: data.error,
  }));

  const isLoading = protocolQueries.some(({ data }) => data.isLoading);
  const error = protocolQueries.find(({ data }) => data.error)?.data.error;

  return {
    protocolsData,
    selectedProtocols: protocols,
    addProtocol,
    removeProtocol,
    resetProtocols,
    isLoading,
    error,
  };
}
