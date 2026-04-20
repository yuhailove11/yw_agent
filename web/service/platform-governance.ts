import { get } from './base'

type SelectableApiServiceItem = {
  resource_code: string
  name: string
  summary?: string
  workspace_id?: string
  route_path?: string
  gateway_url?: string
  resource_type: string
  content: {
    method?: string
    route_path?: string
    url?: string
    summary?: string
    headers_template?: Record<string, string>
    params_schema?: Record<string, unknown>
    body_template?: Record<string, unknown> | string
    timeout?: Record<string, number>
    consumer_auth_required?: boolean
    [key: string]: unknown
  }
}

type SelectableApiServicesResponse = {
  enabled: boolean
  data: SelectableApiServiceItem[]
  total: number
}

export const fetchSelectableApiServices = (): Promise<SelectableApiServicesResponse> => {
  return get('/console/api/platform-governance/api-services/selectable', {}, { silent: true })
}
