export const defaultIcon = '/ui/favicon.ico'

// Showing the letter. / icon
export function isAppIcon(url: string | undefined) {
  return url === defaultIcon ? '' : url
}
