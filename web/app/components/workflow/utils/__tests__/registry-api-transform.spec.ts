import type { RegistryApiNodeType } from '../../nodes/registry-api/types'
import { createNode } from '../../__tests__/fixtures'
import { BodyPayloadValueType, BodyType, Method } from '../../nodes/http/types'
import { BlockEnum } from '../../types'
import { decodeRegistryApiNodes, encodeRegistryApiNodes } from '../registry-api-transform'

describe('registry-api-transform', () => {
  it('should encode registry api nodes to native http request nodes before save', () => {
    const nodes = [
      createNode({
        id: 'registry-node-1',
        data: {
          type: BlockEnum.RegistryApi,
          title: '天气服务',
          desc: '',
          method: Method.post,
          url: 'http://gateway.local/registry/weather/query',
          headers: '{"X-Trace-Id":"demo"}',
          params: '{"city":"hangzhou"}',
          body: {
            type: BodyType.json,
            data: [
              {
                type: BodyPayloadValueType.text,
                value: '{"city":"杭州"}',
              },
            ],
          },
          authorization: {
            type: 'no-auth',
            config: null,
          },
          timeout: {
            connect: 5,
          },
          registry_origin_type: 'registry-api',
          registry_resource_code: 'platform:api_service:weather-query',
          registry_display_name: '天气查询',
          registry_api_config: {
            resource_code: 'platform:api_service:weather-query',
            name: '天气查询',
            gateway_url: 'http://gateway.local/registry/weather/query',
            content: {
              method: 'POST',
            },
          },
        } as Partial<RegistryApiNodeType>,
      }),
    ]

    const encodedNodes = encodeRegistryApiNodes(nodes)
    const encodedData = encodedNodes[0].data as RegistryApiNodeType

    expect(encodedData.type).toBe(BlockEnum.HttpRequest)
    expect(encodedData.registry_origin_type).toBe('registry-api')
    expect(encodedData.registry_http_config).toEqual({
      url: 'http://gateway.local/registry/weather/query',
      method: Method.post,
      headers: '{"X-Trace-Id":"demo"}',
      params: '{"city":"hangzhou"}',
      body: {
        type: BodyType.json,
        data: [
          {
            type: BodyPayloadValueType.text,
            value: '{"city":"杭州"}',
          },
        ],
      },
      timeout: {
        connect: 5,
      },
    })
  })

  it('should decode saved http request nodes back to registry api nodes and normalize legacy body', () => {
    const nodes = [
      createNode({
        id: 'http-node-1',
        data: {
          type: BlockEnum.HttpRequest,
          title: '天气服务',
          desc: '',
          method: Method.post,
          url: 'http://gateway.local/registry/weather/query',
          headers: '{"X-Trace-Id":"demo"}',
          params: '{"city":"hangzhou"}',
          body: {
            type: BodyType.json,
            data: '{"city":"杭州"}',
          },
          authorization: {
            type: 'no-auth',
            config: null,
          },
          timeout: {
            connect: 5,
          },
          registry_origin_type: 'registry-api',
          registry_resource_code: 'platform:api_service:weather-query',
          registry_display_name: '天气查询',
          registry_api_config: {
            resource_code: 'platform:api_service:weather-query',
            name: '天气查询',
            gateway_url: 'http://gateway.local/registry/weather/query',
            content: {
              method: 'POST',
            },
          },
          registry_http_config: {
            url: 'http://gateway.local/registry/weather/query',
            method: 'POST',
            headers: '{"X-Trace-Id":"demo"}',
            params: '{"city":"hangzhou"}',
            body: {
              type: BodyType.json,
              data: '{"city":"杭州"}',
            },
            timeout: {
              connect: 5,
            },
          },
        } as Partial<RegistryApiNodeType>,
      }),
    ]

    const decodedNodes = decodeRegistryApiNodes(nodes)
    const decodedData = decodedNodes[0].data as RegistryApiNodeType

    expect(decodedData.type).toBe(BlockEnum.RegistryApi)
    expect(decodedData.body).toEqual({
      type: BodyType.json,
      data: [
        {
          type: BodyPayloadValueType.text,
          value: '{"city":"杭州"}',
        },
      ],
    })
    expect(decodedData.registry_http_config?.body).toEqual({
      type: BodyType.json,
      data: [
        {
          type: BodyPayloadValueType.text,
          value: '{"city":"杭州"}',
        },
      ],
    })
  })
})
