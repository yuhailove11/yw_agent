import type { FC } from 'react'
import type { RegistryApiNodeType } from './types'
import type { NodePanelProps } from '@/app/components/workflow/types'
import { useQuery } from '@tanstack/react-query'
import { memo, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import Switch from '@/app/components/base/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/base/ui/select'
import Field from '@/app/components/workflow/nodes/_base/components/field'
import OutputVars, { VarItem } from '@/app/components/workflow/nodes/_base/components/output-vars'
import Split from '@/app/components/workflow/nodes/_base/components/split'
import { fetchSelectableApiServices } from '@/service/platform-governance'
import AuthorizationModal from '../http/components/authorization'
import CurlPanel from '../http/components/curl-panel'
import EditBody from '../http/components/edit-body'
import Timeout from '../http/components/timeout'
import useConfig from './use-config'

const i18nPrefix = 'nodes.registryApi'

const Panel: FC<NodePanelProps<RegistryApiNodeType>> = ({
  id,
  data,
}) => {
  const { t } = useTranslation()
  const {
    readOnly,
    isDataReady,
    inputs,
    handleRegistryServiceChange,
    setBody,
    isShowAuthorization,
    showAuthorization,
    hideAuthorization,
    setAuthorization,
    setTimeout,
    isShowCurlPanel,
    showCurlPanel,
    hideCurlPanel,
    handleCurlImport,
    handleSSLVerifyChange,
  } = useConfig(id, data)

  const { data: selectableResponse, isFetching } = useQuery({
    queryKey: ['platform-governance', 'registry-api-services'],
    queryFn: fetchSelectableApiServices,
    staleTime: 60 * 1000,
  })

  const apiServices = selectableResponse?.data || []
  const selectedItem = useMemo(() => {
    return apiServices.find(item => item.resource_code === inputs.registry_resource_code) || null
  }, [apiServices, inputs.registry_resource_code])

  if (!isDataReady)
    return null

  return (
    <div className="pt-2">
      <div className="space-y-4 px-4 pb-4">
        <Field
          title={t(`${i18nPrefix}.service`, { ns: 'workflow' })}
          required
        >
          <Select
            value={inputs.registry_resource_code || ''}
            onValueChange={(value) => {
              const next = apiServices.find(item => item.resource_code === value)
              if (!next)
                return
              handleRegistryServiceChange({
                resource_code: next.resource_code,
                name: next.name,
                summary: next.summary,
                route_path: next.route_path,
                gateway_url: next.gateway_url,
                workspace_id: next.workspace_id,
                content: next.content,
              })
            }}
          >
            <SelectTrigger className="w-full" loading={isFetching} disabled={readOnly}>
              <SelectValue placeholder={t(`${i18nPrefix}.servicePlaceholder`, { ns: 'workflow' })} />
            </SelectTrigger>
            <SelectContent popupClassName="w-[420px]">
              {apiServices.map(item => (
                <SelectItem key={item.resource_code} value={item.resource_code}>
                  {item.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Field>

        <Field title={t(`${i18nPrefix}.summary`, { ns: 'workflow' })}>
          <div className="rounded-lg bg-workflow-block-parma-bg px-3 py-2 text-sm text-text-secondary">
            {selectedItem?.summary || '-'}
          </div>
        </Field>

        <Field title={t(`${i18nPrefix}.gatewayUrl`, { ns: 'workflow' })}>
          <div className="rounded-lg bg-workflow-block-parma-bg px-3 py-2 text-sm break-all text-text-secondary">
            {selectedItem?.gateway_url || inputs.url || '-'}
          </div>
        </Field>

        <Field
          title={t(`${i18nPrefix}.body`, { ns: 'workflow' })}
          required
          operations={(
            <div className="flex items-center gap-2">
              <button type="button" className="text-xs font-medium text-text-tertiary" onClick={showAuthorization}>
                {t(`${i18nPrefix}.authorization`, { ns: 'workflow' })}
              </button>
              <button type="button" className="text-xs font-medium text-text-tertiary" onClick={showCurlPanel}>
                {t(`${i18nPrefix}.import`, { ns: 'workflow' })}
              </button>
            </div>
          )}
        >
          <EditBody
            nodeId={id}
            readonly={readOnly}
            payload={inputs.body}
            onChange={setBody}
          />
        </Field>

        <Field
          title={t(`${i18nPrefix}.verifySSL`, { ns: 'workflow' })}
          operations={(
            <Switch
              value={!!inputs.ssl_verify}
              onChange={handleSSLVerifyChange}
              size="md"
              disabled={readOnly}
            />
          )}
        />
      </div>
      <Split />
      <Timeout
        nodeId={id}
        readonly={readOnly}
        payload={inputs.timeout}
        onChange={setTimeout}
      />
      {(isShowAuthorization && !readOnly) && (
        <AuthorizationModal
          nodeId={id}
          isShow
          onHide={hideAuthorization}
          payload={inputs.authorization}
          onChange={setAuthorization}
        />
      )}
      <Split />
      <div>
        <OutputVars>
          <>
            <VarItem
              name="body"
              type="string"
              description={t('nodes.http.outputVars.body', { ns: 'workflow' })}
            />
            <VarItem
              name="status_code"
              type="number"
              description={t('nodes.http.outputVars.statusCode', { ns: 'workflow' })}
            />
            <VarItem
              name="headers"
              type="object"
              description={t('nodes.http.outputVars.headers', { ns: 'workflow' })}
            />
            <VarItem
              name="files"
              type="Array[File]"
              description={t('nodes.http.outputVars.files', { ns: 'workflow' })}
            />
          </>
        </OutputVars>
      </div>
      {(isShowCurlPanel && !readOnly) && (
        <CurlPanel
          nodeId={id}
          isShow
          onHide={hideCurlPanel}
          handleCurlImport={handleCurlImport}
        />
      )}
    </div>
  )
}

export default memo(Panel)
