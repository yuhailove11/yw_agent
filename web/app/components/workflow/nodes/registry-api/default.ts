import type { NodeDefault } from '../../types'
import type { RegistryApiNodeType } from './types'
import { BlockClassificationEnum } from '@/app/components/workflow/block-selector/types'
import { BlockEnum } from '@/app/components/workflow/types'
import { genNodeMetaData } from '@/app/components/workflow/utils'
import httpDefault from '../http/default'

const metaData = genNodeMetaData({
  classification: BlockClassificationEnum.Utilities,
  sort: 1.1,
  type: BlockEnum.RegistryApi,
  helpLinkUri: 'http-request',
})

const nodeDefault: NodeDefault<RegistryApiNodeType> = {
  ...httpDefault,
  metaData,
  defaultValue: {
    ...httpDefault.defaultValue,
    type: BlockEnum.RegistryApi,
    registry_origin_type: 'registry-api',
    registry_resource_code: '',
    registry_display_name: '',
    registry_api_config: null,
    registry_http_config: null,
  },
}

export default nodeDefault
