interface TeamMember {
  id: string
  username: string
  email: string
  team_id: string
  /**
   * Type of：type：manage owners；
   */
  type: string
  user_id: string
}

export type { TeamMember }
