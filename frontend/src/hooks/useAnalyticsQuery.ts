import { useMutation, useQuery } from 'react-query'
import { useAuth } from './useAuth'
import { TQueryParams, TQueryType } from '../client/types'
import React from 'react';

export const useAnalyticsQuery:React.FC<{qType:TQueryType, qParams: TQueryParams}> = ({qType, qParams}) => {
  
}