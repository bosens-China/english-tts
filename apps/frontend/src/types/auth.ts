export interface UserProfile {
  id: string
  username: string
  display_name: string
  membership: 'free' | 'vip'
  level: number
}

export interface LoginResponse {
  access_token: string
  token_type: 'bearer'
  user: UserProfile
}
