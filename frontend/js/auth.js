import { supabase } from './supabase-client.js'

export async function checkSession() {
  const { data: { session } } = await supabase.auth.getSession()
  return session
}

export async function requireAuth() {
  const session = await checkSession()
  if (!session) {
    if (!window.location.pathname.endsWith('login.html')) {
        window.location.href = 'login.html'
    }
  } else {
    if (window.location.pathname.endsWith('login.html')) {
        window.location.href = 'index.html'
    }
  }
}

export async function logout() {
  await supabase.auth.signOut()
  window.location.href = 'login.html'
}

requireAuth()
