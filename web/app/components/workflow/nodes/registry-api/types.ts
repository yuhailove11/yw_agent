import type { HttpNodeType } from '../http/types'

export type RegistryApiNodeType = HttpNodeType & {
  registry_origin_type?: 'registry-api'
  registry_resource_code?: string
  registry_display_name?: string
  registry_api_config?: {
    resource_code: string
    name: string
    summary?: string
    route_path?: string
    gateway_url?: string
    workspace_id?: string
    content?: Record<string, unknown>
  } | null
  registry_http_config?: {
    url: string
    method: string
    headers: string
    params: string
    body: HttpNodeType['body']
    timeout: HttpNodeType['timeout']
  } | null
}
