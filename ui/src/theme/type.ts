interface ThemeSetting {
  /**
   *element-ui Namespace
   */
  namespace: string;
  /**
   * The data separator.
   */
  division: string;
  /**
   * The Preview
   */
  startDivision: string;
  /**
   * Color Output Setup
   */
  colorInferSetting: ColorInferSetting;
}

/**
 * Colour mix and setting.
 */
interface ColorInferSetting {
  /**
   * with white mix.
   */
  light: Array<number>;
  /**
   * with black mix.
   */
  dark: Array<number>;
  /**
   * Type of
   */
  type: string;
}

/**
 * smooth data
 */
interface KeyValueData {
  [propName: string]: string;
}
type UpdateInferData = KeyValueData;

type UpdateKeyValueData = KeyValueData;
/**
 *smooth data
 */
interface InferData {
  /**
   * set up
   */
  setting?: ColorInferSetting | any;
  /**
   * by Qin
   */
  key: string;
  /**
   * Value
   */
  value: string;
}

export type {
  KeyValueData,
  InferData,
  ThemeSetting,
  UpdateInferData,
  UpdateKeyValueData,
};
