export class Result<T> {
  message: string;
  code: number;
  data: T;
  constructor(message: string, code: number, data: T) {
    this.message = message;
    this.code = code;
    this.data = data;
  }

  static success(data: any) {
    return new Result("Request for Success", 200, data);
  }
  static error(message: string, code: number) {
    return new Result(message, code, null);
  }
}

interface Page<T> {
  /**
   *Separate page data
   */
  records: Array<T>;
  /**
   *Current page
   */
  current: number;
  /**
   * Showing each page.size
   */
  size: number;
  /**
   *The total number
   */
  total: number;
  /**
   *Is there a next page?
   */
  hasNext: boolean;
}
export type { Page };
export default Result;
