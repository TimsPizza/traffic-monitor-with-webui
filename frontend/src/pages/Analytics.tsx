import { useState } from 'react'
import Tables from '../components/Tables'
import { TQueryParams, TQueryType } from '../client/types'

const Analytics = () => {
  const [queryType, setQueryType] = useState<'time' | 'protocol' | 'source-ip'>('time')
  const [queryParams, setQueryParams] = useState<TQueryParams>({
    startTime: 0,
    endTime: 0,
    protocol: '',
    ipAddress: '',
    page: 1,
    pageSize: 50
  })

  const { data, isLoading, isError } = useAnalyticsQuery(queryType, queryParams)

  const handleQuery = (type: TQueryType, params: any) => {
    setQueryType(type)
    setQueryParams(prev => ({ ...prev, ...params }))
  }

  return (
    <div className="p-4">
      <div className="flex gap-4 mb-4">
        <button 
          onClick={() => handleQuery('time', { startTime: Date.now() - 86400000, endTime: Date.now() })}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          Query by Time
        </button>
        <button
          onClick={() => handleQuery('protocol', { protocol: 'TCP' })}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          Query by Protocol
        </button>
        <button
          onClick={() => handleQuery('source-ip', { ipAddress: '192.168.1.1' })}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          Query by Source IP
        </button>
      </div>

      {isLoading && <div>Loading...</div>}
      {isError && <div>Error fetching data</div>}
      {data && <Tables data={data} />}
    </div>
  )
}

export default Analytics
