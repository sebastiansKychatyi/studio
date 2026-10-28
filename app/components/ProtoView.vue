<script setup lang="ts">
import type { PrototypeKind } from '~~/data/prototypes'

defineProps<{ kind: PrototypeKind; preview?: boolean }>()
</script>

<template>
  <ProtoClassifieds v-if="kind === 'classifieds'" :preview="preview" />
  <ProtoBilling v-else-if="kind === 'billing'" :preview="preview" />
  <ProtoCrm v-else-if="kind === 'crm'" :preview="preview" />
  <ProtoReservations v-else-if="kind === 'reservations'" :preview="preview" />
  <ProtoLeads v-else :preview="preview" />
</template>
