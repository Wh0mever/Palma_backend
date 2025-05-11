/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react'

export interface IChildren {
  children: React.ReactNode
}

export interface ISidebarItem {
  icon: React.ReactNode | any
  link?: string | any
  title: string | any
  subNavItems?: { link: string, text: string }[] | any
}

export interface IProductItem {
  image: string
  title: string
  florist?: string
  price?: string | any
  inStock?: any
  isSending?: boolean
  onClick?: (() => void) | null
}

export interface TablesProps {
  data: any
}

export interface FormFieldsProps {
  form: any
  data?: any
}