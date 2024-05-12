import { useLocalStorage } from '@vueuse/core';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import { i18n, langCode, localeConfigKey } from '@/locales/index';

export function useLocale() {
    const { locale } = useI18n({ useScope: 'global' });
    function changeLocale(lang: string) {
        // If the language switched is not in the corresponding language document, the default is simple Chinese.
        if (!langCode.includes(lang)) {
            lang = 'zh_CN';
        }

        locale.value = lang;
        useLocalStorage(localeConfigKey, 'zh_CN').value = lang;
    }

    const getComponentsLocale = computed(() => {
        return i18n.global.getLocaleMessage(locale.value).componentsLocale;
    });

    return {
        changeLocale,
        getComponentsLocale,
        locale,
    };
}
