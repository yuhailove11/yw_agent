import type { BodyType, HttpNodeType, Method } from '../http/types'
import type { RegistryApiNodeType } from './types'
import { useBoolean } from 'ahooks'
import { produce } from 'immer'
import { useCallback, useEffect, useRef } from 'react'
import {
  useNodesReadOnly,
} from '@/app/components/workflow/hooks'
import useNodeCrud from '@/app/components/workflow/nodes/_base/hooks/use-node-crud'
import { normalizeRegistryApiData } from '@/app/components/workflow/utils/registry-api-transform'
import { useStore } from '../../store'
import { BlockEnum } from '../../types'
import { BodyPayloadValueType } from '../http/types'

const normalizeBodyPayload = (bodyTemplate: unknown): RegistryApiNodeType['body'] => {
  const normalizedValue = typeof bodyTemplate === 'string'
    ? bodyTemplate
    : JSON.stringify(bodyTemplate || {}, null, 2)

  return {
    type: 'json' as BodyType,
    data: [
      {
        type: BodyPayloadValueType.text,
        value: normalizedValue,
      },
    ],
  }
}

const useConfig = (id: string, payload: RegistryApiNodeType) => {
  const { nodesReadOnly: readOnly } = useNodesReadOnly()
  const defaultConfig = useStore(s => s.nodesDefaultConfigs?.[BlockEnum.HttpRequest])
  const { inputs, setInputs } = useNodeCrud<RegistryApiNodeType>(id, payload)
  const hasInitializedRef = useRef(false)

  useEffect(() => {
    const isReady = !!defaultConfig && Object.keys(defaultConfig).length > 0
    if (!isReady || hasInitializedRef.current)
      return

    setInputs(normalizeRegistryApiData({
      ...defaultConfig,
      ...inputs,
      type: BlockEnum.RegistryApi,
      registry_origin_type: 'registry-api',
    }))
    hasInitializedRef.current = true
  }, [defaultConfig, inputs, setInputs])

  const isDataReady = hasInitializedRef.current

  const updateInputs = useCallback((updater: (draft: RegistryApiNodeType) => void) => {
    const newInputs = produce(inputs, updater)
    setInputs(newInputs)
  }, [inputs, setInputs])

  const handleMethodChange = useCallback((method: Method) => {
    updateInputs((draft) => {
      draft.method = method
    })
  }, [updateInputs])

  const handleUrlChange = useCallback((url: string) => {
    updateInputs((draft) => {
      draft.url = url
    })
  }, [updateInputs])

  const handleRegistryServiceChange = useCallback((next: RegistryApiNodeType['registry_api_config']) => {
    updateInputs((draft) => {
      const content = next?.content || {}
      draft.registry_origin_type = 'registry-api'
      draft.registry_api_config = next || null
      draft.registry_resource_code = next?.resource_code || ''
      draft.registry_display_name = next?.name || ''
      draft.title = next?.name || draft.title
      draft.method = String(content.method || 'GET').toLowerCase() as RegistryApiNodeType['method']
      draft.url = String(next?.gateway_url || content.gateway_url || content.url || '')
      draft.registry_http_config = {
        url: draft.url,
        method: draft.method,
        headers: JSON.stringify(content.headers_template || {}, null, 2),
        params: JSON.stringify(content.params_schema || {}, null, 2),
        body: normalizeBodyPayload(content.body_template),
        timeout: (content.timeout as HttpNodeType['timeout']) || {},
      }
      draft.headers = draft.registry_http_config.headers
      draft.params = draft.registry_http_config.params
      draft.body = draft.registry_http_config.body
      draft.timeout = draft.registry_http_config.timeout
    })
  }, [updateInputs])

  const [isShowAuthorization, { setTrue: showAuthorization, setFalse: hideAuthorization }] = useBoolean(false)
  const [isShowCurlPanel, { setTrue: showCurlPanel, setFalse: hideCurlPanel }] = useBoolean(false)

  const setAuthorization = useCallback((authorization: RegistryApiNodeType['authorization']) => {
    updateInputs((draft) => {
      draft.authorization = authorization
    })
  }, [updateInputs])

  const setTimeout = useCallback((timeout: RegistryApiNodeType['timeout']) => {
    updateInputs((draft) => {
      draft.timeout = timeout
    })
  }, [updateInputs])

  const setBody = useCallback((body: RegistryApiNodeType['body']) => {
    updateInputs((draft) => {
      draft.body = body
    })
  }, [updateInputs])

  const handleSSLVerifyChange = useCallback((checked: boolean) => {
    updateInputs((draft) => {
      draft.ssl_verify = checked
    })
  }, [updateInputs])

  const handleCurlImport = useCallback((newNode: RegistryApiNodeType) => {
    updateInputs((draft) => {
      draft.method = newNode.method
      draft.url = newNode.url
      draft.headers = newNode.headers
      draft.params = newNode.params
      draft.body = newNode.body
      draft.registry_http_config = {
        url: newNode.url,
        method: newNode.method,
        headers: newNode.headers,
        params: newNode.params,
        body: newNode.body,
        timeout: draft.timeout,
      }
    })
  }, [updateInputs])

  return {
    readOnly,
    isDataReady,
    inputs,
    handleMethodChange,
    handleUrlChange,
    handleRegistryServiceChange,
    isShowAuthorization,
    showAuthorization,
    hideAuthorization,
    setAuthorization,
    setTimeout,
    setBody,
    isShowCurlPanel,
    showCurlPanel,
    hideCurlPanel,
    handleCurlImport,
    handleSSLVerifyChange,
  }
}

export default useConfig
