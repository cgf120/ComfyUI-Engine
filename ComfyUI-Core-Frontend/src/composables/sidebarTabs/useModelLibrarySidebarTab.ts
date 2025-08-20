import { defineAsyncComponent, markRaw } from 'vue'

import ModelLibrarySidebarTab from '@/components/sidebar/tabs/ModelLibrarySidebarTab.vue'
// import { useElectronDownloadStore } from '@/stores/electronDownloadStore' // 已移除
import type { SidebarTabExtension } from '@/types/extensionTypes'
// import { isElectron } from '@/utils/envUtil' // 已移除electron功能

const AiModelIcon = markRaw(
  defineAsyncComponent(() => import('virtual:icons/comfy/ai-model'))
)

export const useModelLibrarySidebarTab = (): SidebarTabExtension => {
  return {
    id: 'model-library',
    icon: AiModelIcon,
    title: 'sideToolbar.modelLibrary',
    tooltip: 'sideToolbar.modelLibrary',
    label: 'sideToolbar.labels.models',
    component: markRaw(ModelLibrarySidebarTab),
    type: 'vue',
    iconBadge: () => {
      // 移除electron下载功能
      // if (isElectron()) {
      //   const electronDownloadStore = useElectronDownloadStore()
      //   if (electronDownloadStore.inProgressDownloads.length > 0) {
      //     return electronDownloadStore.inProgressDownloads.length.toString()
      //   }
      // }

      return null
    }
  }
}
