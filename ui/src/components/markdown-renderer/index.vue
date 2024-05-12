<template>
  <div v-html="inner" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import MarkdownItAbbr from 'markdown-it-abbr'
import MarkdownItAnchor from 'markdown-it-anchor'
import MarkdownItFootnote from 'markdown-it-footnote'
import MarkdownItHighlightjs from 'markdown-it-highlightjs'
import MarkdownItTasklists from 'markdown-it-task-lists'
import MarkdownItSub from 'markdown-it-sub'
import MarkdownItSup from 'markdown-it-sup'
import MarkdownItTOC from 'markdown-it-toc-done-right'

defineOptions({ name: 'MarkdownRenderer' })

const markdownIt = MarkdownIt({
  html: true, // permittedHTMLThe language
  typographer: true, // activatedTypographerAdditional，You can better handle the characters and point symbols.
  linkify: true // automatically in the text.URLConvert to link.
})

markdownIt
  .use(MarkdownItHighlightjs)
  .use(MarkdownItTasklists)
  .use(MarkdownItAbbr)
  .use(MarkdownItAnchor)
  .use(MarkdownItFootnote)
  .use(MarkdownItSub)
  .use(MarkdownItSup)
  .use(MarkdownItTOC)

const props = withDefaults(defineProps<{ source?: string; inner_suffix?: boolean }>(), {
  source: '',
  inner_suffix: false
})

const suffix = '{inner_suffix_' + new Date().getTime() + '}'

const inner = computed(() => {
  if (props.inner_suffix) {
    return markdownIt.render(props.source + suffix).replace(suffix, "<span class='loading'></span>")
  } else {
    return markdownIt.render(props.source)
  }
})
</script>
<style>
.loading:after {
  overflow: hidden;
  display: inline-block;
  vertical-align: bottom;
  animation: ellipsis 0.5s infinite;
  content: '\2026'; /* ascii code for the ellipsis character */
}
@keyframes ellipsis {
  from {
    width: 2px;
  }
  to {
    width: 20px;
  }
}
</style>
