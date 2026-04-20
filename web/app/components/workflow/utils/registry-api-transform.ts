import type { RegistryApiNodeType } from '@/app/components/workflow/nodes/registry-api/types'
import type { Node } from '@/app/components/workflow/types'
import { BodyType } from '@/app/components/workflow/nodes/http/types'
import { transformToBodyPayload } from '@/app/components/workflow/nodes/http/utils'
import { BlockEnum } from '@/app/components/workflow/types'

const isRegistryApiHttpNode = (node: Node) => {
  return node.data.type === BlockEnum.HttpRequest && (node.data as RegistryApiNodeType).registry_origin_type === 'registry-api'
}

const normalizeBody = (body: RegistryApiNodeType['body'] | undefined) => {
  const normalizedType = body?.type || BodyType.none

  if (!body) {
    return {
      type: normalizedType,
      data: [],
    }
  }

  if (typeof body.data === 'string') {
    return {
      ...body,
      type: normalizedType,
      data: transformToBodyPayload(
        body.data,
        [BodyType.formData, BodyType.xWwwFormUrlencoded].includes(normalizedType),
      ),
    }
  }

  return {
    ...body,
    type: normalizedType,
    data: body.data || [],
  }
}

export const normalizeRegistryApiData = (data: RegistryApiNodeType): RegistryApiNodeType => {
  const registryHttpConfig = data.registry_http_config
  const method = String(data.method || registryHttpConfig?.method || 'get').toLowerCase() as RegistryApiNodeType['method']
  const url = data.url || registryHttpConfig?.url || data.registry_api_config?.gateway_url || ''
  const headers = data.headers ?? registryHttpConfig?.headers ?? ''
  const params = data.params ?? registryHttpConfig?.params ?? ''
  const body = normalizeBody(data.body || registryHttpConfig?.body)
  const timeout = data.timeout || registryHttpConfig?.timeout || {}

  return {
    ...data,
    type: BlockEnum.RegistryApi,
    method,
    url,
    headers,
    params,
    body,
    timeout,
    registry_origin_type: 'registry-api',
    registry_http_config: registryHttpConfig
      ? {
          ...registryHttpConfig,
          method,
          url,
          headers,
          params,
          body,
          timeout,
        }
      : data.registry_http_config || null,
  }
}

export const decodeRegistryApiNodes = (nodes: Node[]): Node[] => {
  return nodes.map((node) => {
    if (!isRegistryApiHttpNode(node))
      return node

    return {
      ...node,
      data: normalizeRegistryApiData({
        ...node.data,
        type: BlockEnum.RegistryApi,
      } as RegistryApiNodeType),
    }
  })
}

export const encodeRegistryApiNodes = (nodes: Node[]): Node[] => {
  return nodes.map((node) => {
    if (node.data.type !== BlockEnum.RegistryApi)
      return node

    const data = normalizeRegistryApiData(node.data as RegistryApiNodeType)

    return {
      ...node,
      data: {
        ...data,
        type: BlockEnum.HttpRequest,
        registry_origin_type: 'registry-api',
        registry_http_config: {
          url: data.url,
          method: data.method,
          headers: data.headers,
          params: data.params,
          body: data.body,
          timeout: data.timeout,
        },
      } as RegistryApiNodeType,
    }
  })
}
